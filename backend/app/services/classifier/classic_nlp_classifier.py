import hashlib
import os
import pickle
import re
import logging

import nltk
import numpy as np
import scipy.sparse as sp
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from app.core.interfaces import ClassificationResult, Classifier

# Ensure NLTK data is present once at module load (no repeated network checks in __init__)
for _corpus in ("stopwords", "punkt_tab"):
    nltk.download(_corpus, quiet=True)

_MODEL_CACHE_PATH = os.path.join(os.path.dirname(__file__), "_classic_nlp_cache.pkl")

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Language maps
# ---------------------------------------------------------------------------

# ISO 639-1 → NLTK language name
_LANG_TO_NLTK: dict[str, str] = {
    "pt": "portuguese", "en": "english",  "de": "german",
    "fr": "french",     "es": "spanish",  "it": "italian",
    "nl": "dutch",      "ru": "russian",  "ar": "arabic",
    "da": "danish",     "fi": "finnish",  "hu": "hungarian",
    "no": "norwegian",  "ro": "romanian", "sv": "swedish",
}

# ISO 639-1 → SnowballStemmer language name
_LANG_TO_SNOWBALL: dict[str, str] = _LANG_TO_NLTK.copy()

_DEFAULT_LANG_CODE = "pt"
_DEFAULT_LANG = "portuguese"

# ---------------------------------------------------------------------------
# Low-information detection
# ---------------------------------------------------------------------------

_LOW_INFO_EXACT: frozenset[str] = frozenset({
    "ok", "teste", "test", "hello", "hi", "oi", "olá", "ola",
    "bom dia", "boa tarde", "boa noite", "boas",
    "obrigado", "obrigada", "thanks", "thx", "ty",
    "yes", "no", "sim", "não", "nao",
    "texto qualquer", "qualquer texto", "exemplo", "example",
    "ping", "apenas um teste", "só um teste",
})

# Action words that rescue a short text from low-info classification
_ACTION_WORDS: frozenset[str] = frozenset({
    "preciso", "gostaria", "poderia", "solicito", "ajuda",
    "solicitar", "necessito", "quero", "peço", "pedir",
    "favor", "requer", "necessário", "urgente", "aguardo",
    "consegue", "conseguir", "resolver", "enviar", "envie",
    "atualizar", "verificar", "confirmar", "agendar",
})

_LOW_INFO_MIN_WORDS = 4
_CAT_CONFIDENCE_THRESHOLD = 0.55   # 2 classes  — random baseline = 0.50
_TAG_CONFIDENCE_THRESHOLD = 0.30   # 8 classes  — random baseline = 0.125

# ---------------------------------------------------------------------------
# Feature engineering constants
# ---------------------------------------------------------------------------

_TOKEN_COUNT_NORM = 50.0  # normalisation factor for text_length feature

# ---------------------------------------------------------------------------
# Response templates (deterministic by tag)
# ---------------------------------------------------------------------------

RESPONSE_TEMPLATES: dict[str, str] = {
    "SPAM":
        "Este email foi identificado como conteúdo não relevante e não requer ação.",
    "POSSÍVEL GOLPE":
        "Atenção: este email apresenta características suspeitas. "
        "Não clique em links nem forneça dados pessoais ou credenciais.",
    "URGENTE":
        "Prezado(a), sua mensagem urgente foi recebida. "
        "Nossa equipe foi notificada e retornará o contato com prioridade.",
    "SOLICITAÇÃO":
        "Prezado(a), agradecemos seu contato. "
        "Sua solicitação foi recebida e será analisada em breve.",
    "RECLAMAÇÃO":
        "Lamentamos o ocorrido. "
        "Estamos analisando a situação com prioridade e retornaremos o quanto antes.",
    "REUNIÃO":
        "Prezado(a), confirmamos o recebimento do seu convite. "
        "Retornaremos com nossa disponibilidade em breve.",
    "INFORMATIVO":
        "Agradecemos pelo comunicado. As informações foram registradas.",
    "NÃO IMPORTANTE":
        "Obrigado pela mensagem. Ficamos felizes com o contato.",
}

# ---------------------------------------------------------------------------
# Training dataset (~56 labelled examples — 6-7 per tag + negatives)
# ---------------------------------------------------------------------------

_TRAINING_DATA: list[tuple[str, str, str]] = [
    # --- SPAM ---
    ("Promoção imperdível! Ganhe 50% de desconto em todos os produtos. Oferta válida por tempo limitado. Clique aqui e compre agora!", "Improdutivo", "SPAM"),
    ("Newsletter semanal: confira as novidades do mercado financeiro e as melhores ofertas da semana para você.", "Improdutivo", "SPAM"),
    ("Você foi selecionado para receber um brinde exclusivo. Acesse agora e resgate seu presente gratuito.", "Improdutivo", "SPAM"),
    ("Desconto especial de 70% apenas hoje! Não perca esta oportunidade única de economizar muito.", "Improdutivo", "SPAM"),
    ("Corrente da sorte: encaminhe para 10 amigos e receberá boa sorte. Não quebre a corrente!", "Improdutivo", "SPAM"),
    ("Assine nossa newsletter e receba dicas exclusivas de finanças pessoais toda semana no seu email.", "Improdutivo", "SPAM"),
    ("Black Friday antecipada! Descontos de até 80% em softwares de gestão financeira. Aproveite já!", "Improdutivo", "SPAM"),
    ("Você está recebendo nossa newsletter mensal com as melhores dicas de investimento do mercado.", "Improdutivo", "SPAM"),
    ("Oferta exclusiva para clientes VIP: taxa zero nos primeiros 3 meses. Contrate agora e economize!", "Improdutivo", "SPAM"),
    ("Ganhe R$200 de cashback na sua primeira compra! Cadastre-se gratuitamente e aproveite os benefícios.", "Improdutivo", "SPAM"),
    ("Curso de day trade com 90% de desconto apenas esta semana. Aprenda a lucrar na bolsa de valores!", "Improdutivo", "SPAM"),
    ("Atenção: sua assinatura do pacote premium expira amanhã. Renove agora com 40% de desconto especial.", "Improdutivo", "SPAM"),
    ("Convite exclusivo: participe do nosso webinar gratuito sobre finanças pessoais e investimentos.", "Improdutivo", "SPAM"),
    ("Relatório especial gratuito: os 5 melhores fundos de investimento de 2026. Baixe agora!", "Improdutivo", "SPAM"),
    ("Promoção válida só hoje: plano empresarial com 3 meses grátis. Não deixe para depois!", "Improdutivo", "SPAM"),
    ("Você tem R$150 esperando por você! Resgate agora seu saldo de cashback acumulado.", "Improdutivo", "SPAM"),
    ("Dicas imperdíveis de economia para o mês de março. Confira nosso guia completo no link.", "Improdutivo", "SPAM"),
    ("Seja nosso parceiro e ganhe comissão por cada indicação. Programa de afiliados aberto para novos membros.", "Improdutivo", "SPAM"),
    ("Liquidação de fim de ano: todas as licenças com 60% de desconto. Última chance de aproveitar!", "Improdutivo", "SPAM"),
    ("Alerta de oportunidade: CDB com 130% do CDI disponível por tempo limitado. Invista agora!", "Improdutivo", "SPAM"),

    # --- POSSÍVEL GOLPE ---
    ("URGENTE: sua conta bancária foi suspensa. Clique no link abaixo e atualize seus dados imediatamente para evitar bloqueio.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Parabéns! Você ganhou R$10.000. Para receber, informe seu CPF e dados bancários no formulário.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Verificação de segurança necessária. Acesse http://bit.ly/banco-seguro e confirme sua senha agora.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Seu PIX foi bloqueado por atividade suspeita. Clique aqui para desbloquear informando sua senha.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Oportunidade de investimento: retorno garantido de 300% em 30 dias. Envie seus dados para participar.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Atualização obrigatória do aplicativo do banco. Baixe agora pelo link ou sua conta será encerrada.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Detectamos acesso não autorizado à sua conta. Confirme seus dados no link para proteger seu dinheiro.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Seu token de segurança expirou. Reative agora informando sua senha e número de conta no formulário.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Você foi sorteado como ganhador do prêmio anual de R$50.000. Para resgatar, pague a taxa de R$99.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Ação judicial em seu CPF detectada. Regularize sua situação acessando o link antes de 24h.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Sua conta será encerrada por inatividade. Acesse o link e confirme que ainda deseja mantê-la ativa.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Transferência de R$4.800 realizada em sua conta. Se não reconhece, clique aqui e informe seus dados.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Proposta de parceria: investimento mínimo de R$500 com retorno de 20% ao mês garantido em contrato.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Departamento de Segurança: sua senha foi comprometida. Redefina agora pelo link para evitar prejuízos.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Você tem uma restituição do IR pendente. Informe seus dados bancários para receber R$2.300 em até 3 dias.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Cobrança indevida detectada. Clique no link, informe CPF e senha do banco para solicitar o estorno.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Seu cartão foi clonado. Acesse imediatamente o portal de segurança e bloqueie suas transações.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Oferta especial de crédito pré-aprovado: R$15.000 sem consulta ao SPC. Confirme seus dados agora.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Aviso do Banco Central: regularize seu CPF no sistema financeiro. Prazo: 48 horas. Clique aqui.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Funcionário do banco: preciso de sua ajuda para uma operação interna sigilosa. Não comente com ninguém.", "Improdutivo", "POSSÍVEL GOLPE"),

    # --- URGENTE ---
    ("URGENTE: sistema de pagamentos fora do ar desde as 14h. Clientes não conseguem finalizar transações. Precisamos de resolução imediata.", "Produtivo", "URGENTE"),
    ("Atenção: prazo para entrega do relatório regulatório vence hoje às 17h. Necessito da sua assinatura com urgência.", "Produtivo", "URGENTE"),
    ("Servidor de produção caiu. Todos os serviços estão indisponíveis. Equipe de TI precisa agir imediatamente.", "Produtivo", "URGENTE"),
    ("Reunião de crise convocada para daqui a 30 minutos. Presença obrigatória da diretoria. Assunto: vazamento de dados.", "Produtivo", "URGENTE"),
    ("Prazo regulatório expira amanhã às 09h. Precisamos protocolar os documentos hoje sem falta.", "Produtivo", "URGENTE"),
    ("Cliente VIP ameaça cancelar contrato de R$2M até o fim do dia. Necessária resposta imediata da gerência.", "Produtivo", "URGENTE"),
    ("Falha crítica de segurança identificada no ambiente de produção. Acesso suspeito detectado às 03h14. Ação imediata necessária.", "Produtivo", "URGENTE"),
    ("Auditoria surpresa da CVM programada para amanhã às 08h. Precisamos preparar toda a documentação esta noite.", "Produtivo", "URGENTE"),
    ("Banco central solicitou documentos complementares com prazo de entrega até às 15h de hoje. Favor providenciar.", "Produtivo", "URGENTE"),
    ("Sistema de folha de pagamento travado. Processamento dos salários vence amanhã. TI precisa resolver ainda hoje.", "Produtivo", "URGENTE"),
    ("Erro crítico no fechamento contábil: divergência de R$3,2M detectada. Preciso do controller agora para investigar.", "Produtivo", "URGENTE"),
    ("Decisão judicial exige bloqueio de conta até às 18h. Jurídico e financeiro precisam agir imediatamente.", "Produtivo", "URGENTE"),
    ("Incêndio no datacenter secundário. Ativando plano de continuidade de negócios. Todos os gestores na sala de crise.", "Produtivo", "URGENTE"),
    ("Fornecedor principal cancelou entrega. Produção para em 2 horas sem alternativa. Compras precisa resolver agora.", "Produtivo", "URGENTE"),
    ("Vazamento de dados de clientes confirmado. LGPD exige notificação em até 72h. Jurídico e TI convocados.", "Produtivo", "URGENTE"),
    ("Sistema de trading offline há 20 minutos. Prejuízo estimado de R$800k por hora. Suporte técnico urgente.", "Produtivo", "URGENTE"),
    ("Reunião com investidor principal cancelada se não recebermos o deck revisado em 1 hora. Preciso agora.", "Produtivo", "URGENTE"),
    ("Prazo de compliance com nova regulação encerra hoje. Sem confirmação de adequação a multa é de R$500k.", "Produtivo", "URGENTE"),
    ("Contrato de R$10M não assinado e prazo vence à meia-noite. Diretor jurídico precisa assinar agora.", "Produtivo", "URGENTE"),
    ("SLA de atendimento regulatório violado. Precisamos responder ao BACEN em até 2 horas ou multa é aplicada.", "Produtivo", "URGENTE"),

    # --- SOLICITAÇÃO ---
    ("Gostaria de saber o status do chamado #12345 aberto semana passada referente ao erro no sistema de pagamentos.", "Produtivo", "SOLICITAÇÃO"),
    ("Poderia me enviar o relatório de conciliação bancária do mês de outubro? Preciso para auditoria.", "Produtivo", "SOLICITAÇÃO"),
    ("Solicito acesso ao módulo de relatórios do sistema financeiro para o novo analista João Silva.", "Produtivo", "SOLICITAÇÃO"),
    ("Por favor, preciso de esclarecimentos sobre a política de reembolso de despesas de viagem.", "Produtivo", "SOLICITAÇÃO"),
    ("Você pode reenviar o contrato assinado? Não encontrei o arquivo no email anterior.", "Produtivo", "SOLICITAÇÃO"),
    ("Solicito cotação para renovação do seguro empresarial com vigência a partir de janeiro.", "Produtivo", "SOLICITAÇÃO"),
    ("Poderia verificar o status da transferência realizada ontem? Ainda não foi creditada na conta.", "Produtivo", "SOLICITAÇÃO"),
    ("Preciso de uma segunda via do boleto referente à fatura de fevereiro. Poderia enviar com urgência?", "Produtivo", "SOLICITAÇÃO"),
    ("Gostaria de agendar uma visita técnica para avaliação do nosso parque de servidores. Qual a disponibilidade?", "Produtivo", "SOLICITAÇÃO"),
    ("Solicito a criação de um novo centro de custo no sistema para o departamento de inovação.", "Produtivo", "SOLICITAÇÃO"),
    ("Poderia verificar se a nota fiscal NF-e 00452 foi recebida pelo SEFAZ? Não aparece no sistema.", "Produtivo", "SOLICITAÇÃO"),
    ("Preciso do histórico de transações da conta corrente dos últimos 6 meses para fins de auditoria.", "Produtivo", "SOLICITAÇÃO"),
    ("Solicito aprovação do orçamento de R$45.000 para aquisição de equipamentos de TI conforme proposta anexa.", "Produtivo", "SOLICITAÇÃO"),
    ("Você poderia me informar qual o prazo para liberação do crédito solicitado na semana passada?", "Produtivo", "SOLICITAÇÃO"),
    ("Gostaria de alterar a data de vencimento da minha fatura para o dia 15. É possível fazer isso?", "Produtivo", "SOLICITAÇÃO"),
    ("Solicito treinamento para a equipe no novo módulo de conciliação que entra em produção na próxima semana.", "Produtivo", "SOLICITAÇÃO"),
    ("Preciso de um atestado de capacidade técnica para participação em licitação pública. Podem emitir?", "Produtivo", "SOLICITAÇÃO"),
    ("Poderia confirmar se o pagamento do fornecedor Alfa Ltda foi processado? O prazo venceu ontem.", "Produtivo", "SOLICITAÇÃO"),
    ("Solicito revisão do contrato de prestação de serviços. Há uma cláusula de reajuste que precisa ser atualizada.", "Produtivo", "SOLICITAÇÃO"),
    ("Gostaria de entender melhor as taxas cobradas na minha conta empresarial. Podem detalhar o extrato?", "Produtivo", "SOLICITAÇÃO"),
    ("Preciso cancelar o agendamento de débito automático referente ao contrato #4872. Como procedo?", "Produtivo", "SOLICITAÇÃO"),
    ("Você pode me enviar o manual do usuário do sistema de gestão de fornecedores? Não encontro no portal.", "Produtivo", "SOLICITAÇÃO"),
    ("Solicito a inclusão do funcionário Carlos Mendes no plano de saúde empresarial a partir de 01/04.", "Produtivo", "SOLICITAÇÃO"),
    ("Preciso de esclarecimento sobre a nova política de aprovação de despesas acima de R$5.000.", "Produtivo", "SOLICITAÇÃO"),
    ("Poderia me informar o contato do responsável técnico pelo sistema de DRE automatizado?", "Produtivo", "SOLICITAÇÃO"),

    # --- RECLAMAÇÃO ---
    ("Estou muito insatisfeito com o serviço prestado. O prazo foi descumprido pela terceira vez consecutiva.", "Produtivo", "RECLAMAÇÃO"),
    ("O sistema continua apresentando erros mesmo após a manutenção prometida. Isto é inaceitável.", "Produtivo", "RECLAMAÇÃO"),
    ("Minha fatura apresentou cobranças indevidas no valor de R$500. Exijo estorno imediato e explicação.", "Produtivo", "RECLAMAÇÃO"),
    ("O atendimento da equipe de suporte foi extremamente insatisfatório. Abro reclamação formal.", "Produtivo", "RECLAMAÇÃO"),
    ("Já solicitei 3 vezes o cancelamento e o serviço continua sendo cobrado. Situação inadmissível.", "Produtivo", "RECLAMAÇÃO"),
    ("Produto entregue com defeito e a equipe de suporte se recusa a providenciar a troca. Registro reclamação.", "Produtivo", "RECLAMAÇÃO"),
    ("Estou formalizando reclamação pelo não cumprimento do SLA contratado. Já foram 48h sem resposta.", "Produtivo", "RECLAMAÇÃO"),
    ("A consultoria entregou o relatório com dados incorretos pela segunda vez. Exijo revisão sem custo adicional.", "Produtivo", "RECLAMAÇÃO"),
    ("Fui cobrado em duplicidade na fatura de março. Quero o estorno imediato e uma explicação por escrito.", "Produtivo", "RECLAMAÇÃO"),
    ("O sistema apresenta lentidão crônica desde a última atualização. Produtividade da equipe foi severamente impactada.", "Produtivo", "RECLAMAÇÃO"),
    ("A proposta enviada não corresponde ao que foi acordado em reunião. Isso é desrespeito ao cliente.", "Produtivo", "RECLAMAÇÃO"),
    ("Meu pedido de reembolso foi negado sem justificativa após 3 semanas de análise. Exijo revisão imediata.", "Produtivo", "RECLAMAÇÃO"),
    ("O técnico não compareceu na janela de manutenção agendada e ninguém nos avisou. Situação inaceitável.", "Produtivo", "RECLAMAÇÃO"),
    ("Dados da minha empresa foram expostos em relatório enviado a terceiros sem nossa autorização. Exijo providências.", "Produtivo", "RECLAMAÇÃO"),
    ("O suporte demorou 5 dias para responder uma dúvida simples. Este nível de atendimento é inaceitável.", "Produtivo", "RECLAMAÇÃO"),
    ("Contrato com previsão de início em janeiro ainda não foi formalizado. Estamos em março. Que explicação têm?", "Produtivo", "RECLAMAÇÃO"),
    ("Recebi notificação de protesto indevido. Nunca estive em débito com vocês. Exijo cancelamento imediato.", "Produtivo", "RECLAMAÇÃO"),
    ("O sistema de emissão de NF está com erros desde segunda-feira. Já registrei 4 chamados sem solução.", "Produtivo", "RECLAMAÇÃO"),
    ("Fui mal atendido pelo gerente da conta durante reunião. Comportamento inadequado que formalizo aqui.", "Produtivo", "RECLAMAÇÃO"),
    ("A implementação do sistema atrasou 2 meses sem comunicação prévia, causando prejuízo operacional.", "Produtivo", "RECLAMAÇÃO"),

    # --- REUNIÃO ---
    ("Convido para reunião de alinhamento sobre o projeto de transformação digital na próxima terça-feira às 10h.", "Produtivo", "REUNIÃO"),
    ("Confirmo presença na reunião de diretoria marcada para sexta-feira às 14h na sala de conferências.", "Produtivo", "REUNIÃO"),
    ("Podemos agendar uma call para discutir os resultados do terceiro trimestre? Sugiro quinta às 15h.", "Produtivo", "REUNIÃO"),
    ("Convocação para reunião extraordinária do conselho administrativo em 20/03 às 09h.", "Produtivo", "REUNIÃO"),
    ("Você tem disponibilidade para um café na próxima semana para discutirmos a parceria?", "Produtivo", "REUNIÃO"),
    ("Segue o convite para o webinar sobre compliance regulatório. Confirme sua participação.", "Produtivo", "REUNIÃO"),
    ("Gostaria de agendar uma reunião de kick-off para o novo projeto. Qual a sua disponibilidade esta semana?", "Produtivo", "REUNIÃO"),
    ("Convite: apresentação dos resultados anuais para o board na quarta-feira às 09h. Confirme presença até amanhã.", "Produtivo", "REUNIÃO"),
    ("Precisamos marcar uma call com o cliente ABC para discutir a renovação do contrato. Quando você pode?", "Produtivo", "REUNIÃO"),
    ("Segue calendário das reuniões de planejamento do Q2. Por favor, bloqueie as datas na sua agenda.", "Produtivo", "REUNIÃO"),
    ("Você toparia um almoço de trabalho na quinta para discutirmos os ajustes no escopo do projeto?", "Produtivo", "REUNIÃO"),
    ("Convocação: revisão do orçamento 2026 com todos os gestores de área na sala Executiva, segunda às 08h.", "Produtivo", "REUNIÃO"),
    ("Preciso agendar uma reunião de 1:1 com você ainda esta semana. Tenho pontos importantes para discutir.", "Produtivo", "REUNIÃO"),
    ("Você pode participar de uma call amanhã às 11h para alinhar os próximos passos da auditoria?", "Produtivo", "REUNIÃO"),
    ("Convite para workshop de estratégia: 25/03, das 09h às 17h, Hotel Blue Tree. Confirme participação.", "Produtivo", "REUNIÃO"),
    ("Reunião de retrospectiva do sprint marcada para sexta às 16h. Favor confirmar presença até quinta.", "Produtivo", "REUNIÃO"),
    ("Agendei uma demo do novo sistema com o fornecedor para segunda às 14h. Você pode participar?", "Produtivo", "REUNIÃO"),
    ("Convocação para comitê de risco extraordinário: amanhã às 16h, sala 3B. Pauta: exposição cambial.", "Produtivo", "REUNIÃO"),
    ("Você teria 30 minutos esta semana para uma call de apresentação da nossa solução de BI?", "Produtivo", "REUNIÃO"),
    ("Confirmo o agendamento: entrevista de feedback com RH na terça às 10h30, sala Recursos Humanos.", "Produtivo", "REUNIÃO"),

    # --- INFORMATIVO ---
    ("Informamos que o sistema estará em manutenção programada no sábado das 02h às 06h.", "Improdutivo", "INFORMATIVO"),
    ("Comunicado: a partir de 01/04, o horário de atendimento será das 08h às 18h de segunda a sexta.", "Improdutivo", "INFORMATIVO"),
    ("Aviso: nova política de senhas entra em vigor na próxima semana. Todos devem atualizar seus acessos.", "Improdutivo", "INFORMATIVO"),
    ("Nota informativa: o escritório estará fechado nos dias 20 e 21 de março em razão do feriado municipal.", "Improdutivo", "INFORMATIVO"),
    ("Atualização do sistema ERP prevista para o próximo final de semana. Backup realizado automaticamente.", "Improdutivo", "INFORMATIVO"),
    ("Comunicado interno: mudança de endereço da matriz a partir de 01/05. Novo endereço em anexo.", "Improdutivo", "INFORMATIVO"),
    ("Informamos que a versão 3.2 do sistema de gestão financeira foi implantada com sucesso nesta madrugada.", "Improdutivo", "INFORMATIVO"),
    ("Nota à equipe: o refeitório estará fechado para reforma entre os dias 10 e 20 de abril.", "Improdutivo", "INFORMATIVO"),
    ("Comunicado RH: o banco de horas referente ao primeiro trimestre foi apurado e enviado aos gestores.", "Improdutivo", "INFORMATIVO"),
    ("Aviso de segurança: detectamos tentativas de phishing usando o nome da empresa. Não clique em links suspeitos.", "Improdutivo", "INFORMATIVO"),
    ("Informativo: a certificação ISO 27001 da empresa foi renovada com sucesso pelo próximo triênio.", "Improdutivo", "INFORMATIVO"),
    ("Comunicado: em razão do feriado de Páscoa, o expediente do dia 18/04 será encerrado às 14h.", "Improdutivo", "INFORMATIVO"),
    ("Nota interna: o processo de aprovação de fornecedores passou a exigir validação do jurídico a partir desta semana.", "Improdutivo", "INFORMATIVO"),
    ("Informamos que o relatório de resultados do Q1/2026 foi publicado no portal interno. Acesse para consulta.", "Improdutivo", "INFORMATIVO"),
    ("Aviso: as novas diretrizes de governança corporativa entram em vigor em 01/05. Material disponível na intranet.", "Improdutivo", "INFORMATIVO"),
    ("Comunicado TI: a VPN corporativa passará a exigir autenticação de dois fatores a partir de segunda-feira.", "Improdutivo", "INFORMATIVO"),
    ("Informativo financeiro: a taxa de câmbio de referência utilizada internamente foi atualizada para R$5,87/USD.", "Improdutivo", "INFORMATIVO"),
    ("Nota de boas-vindas ao novo diretor comercial, Paulo Henrique, que inicia na próxima segunda-feira.", "Improdutivo", "INFORMATIVO"),
    ("Comunicado: o estacionamento do bloco B estará interditado para obras entre os dias 22 e 28 de março.", "Improdutivo", "INFORMATIVO"),
    ("Aviso aos gestores: o ciclo de avaliação de desempenho semestral será aberto na plataforma na próxima semana.", "Improdutivo", "INFORMATIVO"),

    # --- NÃO IMPORTANTE ---
    ("Feliz Natal a todos da equipe! Que 2026 seja repleto de conquistas e realizações para todos.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Obrigado pelo excelente atendimento de ontem! Fico muito satisfeito com a qualidade do serviço.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Bom fim de semana a todos! Aproveitem o descanso merecido após uma semana produtiva.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Parabéns pela promoção! Você merece muito este reconhecimento pelo seu trabalho dedicado.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Agradecemos a parceria ao longo desses anos. Esperamos continuar crescendo juntos.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Boa semana para todos! Que seja cheia de produtividade e boas notícias para a equipe.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Só passando para agradecer pelo apoio durante o projeto. A equipe foi incrível do começo ao fim.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Parabéns pelo aniversário da empresa! 20 anos de muito trabalho e conquistas. Que venham mais 20!", "Improdutivo", "NÃO IMPORTANTE"),
    ("Obrigado pelo feedback na apresentação de ontem. Suas observações foram muito valiosas.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Desejamos uma excelente viagem à família toda! Aproveitem as férias e voltem com energia renovada.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Foi um prazer participar da reunião com vocês. Equipe muito capacitada e comprometida.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Parabéns pelo resultado do trimestre! A equipe de vendas arrasou. Merecido reconhecimento.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Muito obrigada pelo apoio de sempre. É um prazer trabalhar com profissionais tão dedicados.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Feliz aniversário! Que este novo ano de vida seja repleto de saúde, alegria e realizações.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Boa tarde a todos! Espero que estejam bem. Qualquer novidade eu apareço por aqui.", "Improdutivo", "NÃO IMPORTANTE"),
    ("ok tudo certo pode fechar", "Improdutivo", "NÃO IMPORTANTE"),
    ("teste de envio do sistema de emails corporativos", "Improdutivo", "NÃO IMPORTANTE"),
    ("olá tudo bem com você hoje", "Improdutivo", "NÃO IMPORTANTE"),
    ("bom dia para toda a equipe presente", "Improdutivo", "NÃO IMPORTANTE"),
    ("obrigado pela sua atenção e apoio", "Improdutivo", "NÃO IMPORTANTE"),
    ("apenas verificando se o email está funcionando corretamente", "Improdutivo", "NÃO IMPORTANTE"),
    ("ok pode seguir em frente com o processo", "Improdutivo", "NÃO IMPORTANTE"),
    ("recebido obrigado", "Improdutivo", "NÃO IMPORTANTE"),
    ("certo entendido vou verificar depois", "Improdutivo", "NÃO IMPORTANTE"),
    ("boa tarde tudo bem por aí", "Improdutivo", "NÃO IMPORTANTE"),

    # --- English examples (one per tag for cross-lingual coverage) ---
    ("Hi support team, could you please check the status of invoice #892? Payment was sent last week but still shows pending.", "Produtivo", "SOLICITAÇÃO"),
    ("URGENT: production server is down since 3pm. All transactions are failing. We need immediate action from the infrastructure team.", "Produtivo", "URGENTE"),
    ("I am formally complaining about the repeated service outages this month. This is unacceptable and I demand a resolution.", "Produtivo", "RECLAMAÇÃO"),
    ("Could we schedule a call this week to discuss the Q2 results? I suggest Thursday at 2pm.", "Produtivo", "REUNIÃO"),
    ("Exclusive offer! Get 60% off all financial management tools today only. Click here to claim your discount now!", "Improdutivo", "SPAM"),
    ("WARNING: your account has been suspended. Click the link below to verify your credentials immediately or your account will be closed.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Please be informed that the system will undergo scheduled maintenance on Saturday from 2am to 6am. No action required.", "Improdutivo", "INFORMATIVO"),
    ("Thank you so much for your help yesterday. It was a pleasure working with such a dedicated team. Have a great weekend!", "Improdutivo", "NÃO IMPORTANTE"),
]


# ---------------------------------------------------------------------------
# Standalone heuristic (importable / testable independently)
# ---------------------------------------------------------------------------

def is_low_information(text: str) -> bool:
    """Return True when the text carries no classifiable intent.

    Rules (applied in order):
    1. Empty / whitespace-only.
    2. Exact match against known low-info phrases.
    3. Fewer than _LOW_INFO_MIN_WORDS tokens AND no action words detected.
    """
    stripped = text.strip().lower()
    if not stripped:
        return True

    if stripped in _LOW_INFO_EXACT:
        return True

    tokens = re.findall(r"\b\w+\b", stripped)
    if len(tokens) < _LOW_INFO_MIN_WORDS:
        if any(t in _ACTION_WORDS for t in tokens):
            return False  # short but has clear intent — not low-info
        return True

    return False


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

class ClassicNLPClassifier(Classifier):
    """Email classifier using a classic NLP pipeline (Strategy Pattern).

    Pipeline:
      0. Low-information heuristic (fast path — no ML needed)
      1. Language detection (stopword-based, PT/EN)
      2. Stopword removal + SnowballStemmer (NLTK)
      3. TF-IDF (1-2 ngrams) + engineered features → combined sparse matrix
      4. Logistic Regression for category + tag (scikit-learn, predict_proba)
      5. Confidence threshold: if max(proba) < 0.6 → force Improdutivo/NÃO IMPORTANTE
      6. Extractive summarisation via TF-IDF sentence scoring
      7. Deterministic template-based response generation
    """

    def __init__(self) -> None:
        # Pre-load stopword sets used by the fast language detector
        self._sw_pt: set[str] = set(stopwords.words("portuguese"))
        self._sw_en: set[str] = set(stopwords.words("english"))

        data_hash = self._training_hash()
        if self._load_cache(data_hash):
            logger.info("ClassicNLPClassifier loaded from cache | vocab_size=%d", len(self._vectorizer.vocabulary_))
            return

        texts, categories, tags = zip(*_TRAINING_DATA)
        processed = [self._nlp_preprocess(t) for t in texts]

        self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=1500)
        X_tfidf = self._vectorizer.fit_transform(processed)
        X_extra = sp.csr_matrix(self._extra_features(list(texts)))
        X = sp.hstack([X_tfidf, X_extra])

        self._cat_clf = LogisticRegression(max_iter=1000, random_state=42)
        self._cat_clf.fit(X, categories)

        self._tag_clf = LogisticRegression(max_iter=1000, random_state=42)
        self._tag_clf.fit(X, tags)

        self._save_cache(data_hash)
        logger.info(
            "ClassicNLPClassifier trained | training_samples=%d | vocab_size=%d",
            len(texts), len(self._vectorizer.vocabulary_),
        )

    # ------------------------------------------------------------------
    # Model cache helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _training_hash() -> str:
        payload = repr(_TRAINING_DATA).encode()
        return hashlib.md5(payload).hexdigest()

    def _load_cache(self, data_hash: str) -> bool:
        if not os.path.exists(_MODEL_CACHE_PATH):
            return False
        try:
            with open(_MODEL_CACHE_PATH, "rb") as f:
                cached = pickle.load(f)
            if cached.get("hash") != data_hash:
                return False
            self._vectorizer = cached["vectorizer"]
            self._cat_clf    = cached["cat_clf"]
            self._tag_clf    = cached["tag_clf"]
            return True
        except Exception as e:
            logger.warning("Cache load failed (%s) — retraining", e)
            return False

    def _save_cache(self, data_hash: str) -> None:
        try:
            with open(_MODEL_CACHE_PATH, "wb") as f:
                pickle.dump({
                    "hash":       data_hash,
                    "vectorizer": self._vectorizer,
                    "cat_clf":    self._cat_clf,
                    "tag_clf":    self._tag_clf,
                }, f)
        except Exception as e:
            logger.warning("Cache save failed: %s", e)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def classify(self, text: str) -> ClassificationResult:
        logger.info("ClassicNLPClassifier.classify() | text_length=%d", len(text))

        # --- Step 0: low-information fast path ---
        if is_low_information(text):
            logger.info("Low-information input detected — returning NÃO IMPORTANTE")
            return ClassificationResult(
                category="Improdutivo",
                tag="NÃO IMPORTANTE",
                summary=text.strip()[:150] or "Mensagem sem conteúdo relevante.",
                suggested_response=RESPONSE_TEMPLATES["NÃO IMPORTANTE"],
            )

        # --- Steps 1-3: preprocess + build feature matrix ---
        processed = self._nlp_preprocess(text)
        X_tfidf = self._vectorizer.transform([processed])
        X_extra = sp.csr_matrix(self._extra_features([text]))
        X = sp.hstack([X_tfidf, X_extra])

        # --- Step 4: predict with probabilities ---
        cat_proba = self._cat_clf.predict_proba(X)[0]
        tag_proba = self._tag_clf.predict_proba(X)[0]

        cat_confidence = float(cat_proba.max())
        tag_confidence = float(tag_proba.max())

        # --- Step 5: confidence threshold fallback (separate thresholds per classifier) ---
        # Category has 2 classes (random baseline = 0.50) → threshold 0.55
        # Tag has 8 classes (random baseline = 0.125) → threshold 0.30
        cat_ok = cat_confidence >= _CAT_CONFIDENCE_THRESHOLD
        tag_ok = tag_confidence >= _TAG_CONFIDENCE_THRESHOLD

        _TAG_TO_CATEGORY = {
            "URGENTE": "Produtivo", "SOLICITAÇÃO": "Produtivo",
            "RECLAMAÇÃO": "Produtivo", "REUNIÃO": "Produtivo",
            "SPAM": "Improdutivo", "POSSÍVEL GOLPE": "Improdutivo",
            "INFORMATIVO": "Improdutivo", "NÃO IMPORTANTE": "Improdutivo",
        }

        if not tag_ok:
            logger.info("Low tag confidence (%.2f) — forcing NÃO IMPORTANTE", tag_confidence)
            tag = "NÃO IMPORTANTE"
        else:
            tag = str(self._tag_clf.classes_[tag_proba.argmax()])

        # Derive category from tag when confident; fall back to category classifier
        if tag_ok:
            category = _TAG_TO_CATEGORY.get(tag, "Improdutivo")
        elif cat_ok:
            category = str(self._cat_clf.classes_[cat_proba.argmax()])
        else:
            logger.info("Low confidence on both classifiers — forcing Improdutivo", )
            category = "Improdutivo"

        summary = self._summarize(text)
        suggested_response = RESPONSE_TEMPLATES.get(tag, RESPONSE_TEMPLATES["INFORMATIVO"])

        logger.info(
            "Classic result: category=%s, tag=%s, cat_conf=%.2f, tag_conf=%.2f",
            category, tag, cat_confidence, tag_confidence,
        )
        return ClassificationResult(
            category=category,
            tag=tag,
            summary=summary,
            suggested_response=suggested_response,
        )

    # ------------------------------------------------------------------
    # Feature engineering
    # ------------------------------------------------------------------

    def _extra_features(self, texts: list[str]) -> np.ndarray:
        """Compute lightweight handcrafted features alongside TF-IDF.

        Features (per text):
          - text_length:       normalised token count (capped at 1.0)
          - has_question_mark: 1 if '?' present, else 0
          - has_action_words:  1 if any action word found, else 0
        """
        rows: list[list[float]] = []
        for t in texts:
            tokens = re.findall(r"\b\w+\b", t.lower())
            rows.append([
                min(len(tokens) / _TOKEN_COUNT_NORM, 1.0),
                float("?" in t),
                float(any(tok in _ACTION_WORDS for tok in tokens)),
            ])
        return np.array(rows, dtype=float)

    # ------------------------------------------------------------------
    # NLP preprocessing
    # ------------------------------------------------------------------

    def _detect_lang_code(self, text: str) -> str:
        """Fast stopword-based language detection (PT vs EN); default 'pt'.

        Counts how many lowercased tokens match each stopword set.
        Runs in O(n) with no external calls — ~0.1ms vs ~7ms for langdetect.
        """
        tokens = re.findall(r"\b[a-z]+\b", text.lower())
        if not tokens:
            return _DEFAULT_LANG_CODE
        score_pt = sum(1 for t in tokens if t in self._sw_pt)
        score_en = sum(1 for t in tokens if t in self._sw_en)
        return "en" if score_en > score_pt else "pt"

    def _nlp_preprocess(self, text: str) -> str:
        """Lowercase → remove punctuation → remove stopwords → stem."""
        lang_code = self._detect_lang_code(text)
        nltk_lang = _LANG_TO_NLTK.get(lang_code, _DEFAULT_LANG)
        snowball_lang = _LANG_TO_SNOWBALL.get(lang_code, _DEFAULT_LANG)

        try:
            sw = set(stopwords.words(nltk_lang))
        except OSError:
            sw = set(stopwords.words(_DEFAULT_LANG))

        try:
            stemmer = SnowballStemmer(snowball_lang)
        except Exception:
            stemmer = SnowballStemmer(_DEFAULT_LANG)

        tokens = re.findall(r"\b\w+\b", text.lower())
        stemmed = [stemmer.stem(t) for t in tokens if t not in sw and len(t) > 1]
        return " ".join(stemmed)

    # ------------------------------------------------------------------
    # Extractive summarisation
    # ------------------------------------------------------------------

    def _summarize(self, text: str) -> str:
        """Pick the sentence with highest mean TF-IDF score."""
        sentences = [s.strip() for s in sent_tokenize(text) if len(s.strip()) > 10]
        if not sentences:
            return text.strip()[:150]
        if len(sentences) == 1:
            return sentences[0][:200]

        X = self._vectorizer.transform(sentences)
        scores = X.toarray().mean(axis=1)
        return sentences[int(scores.argmax())][:250]

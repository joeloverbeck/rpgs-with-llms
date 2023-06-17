from sentence_transformers import SentenceTransformer

MODEL = SentenceTransformer("paraphrase-MiniLM-L6-v2")

GPT_3_5 = "gpt-3.5-turbo-0613"
GPT_4 = "gpt-4-0613"

DEFAULT_TEMPERATURE = 0.7
MAX_TOKENS = 2048

SYSTEM_ROLE = "system"
ASSISTANT_ROLE = "assistant"
USER_ROLE = "user"

VECTOR_DIMENSIONS = 384
NUMBER_OF_TREES = 10
METRIC_ANGULAR = "angular"
DECAY_RATE = 0.99

NUMBER_OF_BASE_RESULTS_FOR_EVERY_QUERY = 50

SCORE_ALPHA = 1.0
SCORE_BETA = 1.0
SCORE_GAMMA = 1.0

INSTRUCT_GPT_PROMPT_HEADER = "Question. "
INSTRUCT_GPT_PROMPT_ANSWER_OPENING = (
    " Answer: Let's try to work out the answer step by step: "
)

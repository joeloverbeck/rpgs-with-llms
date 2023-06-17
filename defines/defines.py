from sentence_transformers import SentenceTransformer

MODEL = SentenceTransformer("paraphrase-MiniLM-L6-v2")

GPT_3_5 = "gpt-3.5-turbo-0613"
GPT_4 = "gpt-4-0613"

DEFAULT_TEMPERATURE = 0.7
MAX_TOKENS = 2048

SYSTEM_ROLE = "system"
ASSISTANT_ROLE = "assistant"

DIALOGUE_GPT_SYSTEM_CONTENT = "I am DialogueGPT. I have the responsibility of carrying on a dialogue between two or more characters until the context of "
DIALOGUE_GPT_SYSTEM_CONTENT += "the dialogue suggests that the dialogue should end."
STOP_DIALOGUE_FUNCTION_NAME = "stop_dialogue"
STOP_DIALOGUE_FUNCTION_DESCRIPTION = "Stops the dialogue if the latest utterances make it appropriate for the dialogue to end now."
WRITE_LINES_OF_DIALOGUE_FUNCTION_NAME = "write_lines_of_dialogue"
WRITE_LINES_OF_DIALOGUE_FUNCTION_DESCRIPTION = (
    "Writes the next line of dialogue for one of the characters involved, "
)
WRITE_LINES_OF_DIALOGUE_FUNCTION_DESCRIPTION += (
    "that realistically would speak at this point of the dialogue."
)
LINES_OF_DIALOGUE_PARAMETER_NAME = "lines_of_dialogue"
LINES_OF_DIALOGUE_PARAMETER_DESCRIPTION = "A line of dialogue, starting with the name of the character, followed by a colon and the spoken line of dialogue."
LINES_OF_DIALOGUE_PARAMETER_DESCRIPTION += " Can also include narration in parenthesis, if necessary. Never repeat the last line of dialogue."

HOW_MANY_LINES_OF_DIALOGUE_TO_SHOW_TO_USER = 4

VECTOR_DIMENSIONS = 384
NUMBER_OF_TREES = 10
METRIC_ANGULAR = "angular"
DECAY_RATE = 0.99

SCORE_ALPHA = 1.0
SCORE_BETA = 1.0
SCORE_GAMMA = 1.0

INSTRUCT_GPT_PROMPT_HEADER = "Question. "
INSTRUCT_GPT_PROMPT_ANSWER_OPENING = (
    " Answer: Let's try to work out the answer step by step: "
)

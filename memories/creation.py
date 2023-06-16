from defines.defines import NUMBER_OF_TREES
from errors import UnableToSaveVectorDatabaseError


def create_vector_database(memories_full_path, new_index):
    new_index.build(NUMBER_OF_TREES)

    try:
        new_index.save(memories_full_path)
    except OSError as exception:
        message_error = f"The function {create_vector_database.__name__} was unable to save the vector database at {memories_full_path}."
        message_error += f" Error: {exception}"

        raise UnableToSaveVectorDatabaseError(message_error) from exception

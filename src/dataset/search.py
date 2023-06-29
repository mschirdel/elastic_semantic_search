import os
from sentence_transformers import SentenceTransformer

print("Starting up the models...")
def startup():
    # note tokenizer is not needed the sentence transformers apply the tokenization
    # note langchain model is much easier to use, and it can unify towards using the llms too 
    MODEL_NAME = "sentence-transformers/all-mpnet-base-v2" # this is the best model for semantic search
    model = SentenceTransformer(MODEL_NAME)
    return model 


def perform_search(query, model=startup()):
    # Perform transformations on the input query
    transformed_query = query.upper()  # Example transformation: Convert query to uppercase

    print(model.get_sentence_embedding_dimension())
    # Generate results based on the transformed query
    # Replace the following lines with your own logic and processing based on the transformed query
    results = [
        f"Result 1: {transformed_query} - Some information",
        f"Result 2: {transformed_query} - More details",
        f"Result 3: {transformed_query} - Additional data"
    ]

    # Return the results
    return results

def clear_screen():
    # Clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

# Main search system CLI loop
while True:
    # Accept input query from the command line
    query = input("Enter your query (or 'exit' to quit): ")

    # Check if the user wants to exit
    if query.lower() == "exit":
        print("Exiting...")
        break

    # Clear the terminal screen
    clear_screen()

    # Perform the search and get the results
    results = perform_search(query)

    # Print the results
    print("Results:")
    for result in results:
        print(result)
    print()

    # Prompt the user to press Enter to continue
    input("Press Enter to continue...")
    clear_screen()

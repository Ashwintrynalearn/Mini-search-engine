from app.indexing.indexer import load_documents, build_inverted_index
from app.search.search_service import search


DOCS_DIR = "data/docs"


def main() -> None:
    documents = load_documents(DOCS_DIR)
    inverted_index = build_inverted_index(documents)

    print("Mini Search Engine")
    print(f"Loaded {len(documents)} documents.")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("Search query: ").strip()

        if query.lower() == "exit":
            print("Goodbye!")
            break

        if not query:
            print("Please enter a search query.\n")
            continue

        results = search(query, inverted_index)

        if not results:
            print("No results found.\n")
            continue

        print("\nResults:")
        for rank, (document_name, score) in enumerate(results, start=1):
            print(f"{rank}. {document_name} | score: {score}")

        print()


if __name__ == "__main__":
    main()
from app.indexing.indexer import (
    load_documents,
    build_inverted_index,
    build_document_stats,
)
from app.search.search_service import search
from app.search.snippet import generate_snippet


DOCS_DIR = "data/docs"


def main() -> None:
    documents = load_documents(DOCS_DIR)
    inverted_index = build_inverted_index(documents)
    document_stats = build_document_stats(documents)

    print("Mini Search Engine")
    print(f"Loaded {len(documents)} documents.")
    print(f"Indexed {len(inverted_index)} unique terms.")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("Search query: ").strip()

        if query.lower() == "exit":
            print("Goodbye!")
            break

        if not query:
            print("Please enter a search query.\n")
            continue

        results = search(
            query=query,
            inverted_index=inverted_index,
            total_documents=len(documents),
        )

        if not results:
            print("No results found.\n")
            continue

        print("\nResults:")
        for rank, (document_name, score) in enumerate(results, start=1):
            snippet = generate_snippet(
                content=documents[document_name],
                query=query,
            )

            doc_length = document_stats[document_name]["length"]

            print(f"{rank}. {document_name} | score: {score:.4f} | length: {doc_length}")
            print(f"   {snippet}")

        print()


if __name__ == "__main__":
    main()
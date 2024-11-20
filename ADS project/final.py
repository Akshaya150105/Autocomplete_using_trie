import time
import streamlit as st
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

ALPHABET_SIZE = 36

def char_to_index(c):
    if 'a' <= c <= 'z':
        return ord(c) - ord('a')
    elif '0' <= c <= '9':
        return ord(c) - ord('0') + 26
    else:
        return None

class TrieNode:
    def __init__(self):
        self.children = [None] * ALPHABET_SIZE
        self.isWordEnd = False

def get_node():
    return TrieNode()

def insert(root, key):
    pCrawl = root
    key = key.lower()
    for level in range(len(key)):
        index = char_to_index(key[level])
        if index is not None:
            if not pCrawl.children[index]:
                pCrawl.children[index] = get_node()
            pCrawl = pCrawl.children[index]
    pCrawl.isWordEnd = True

def suggestions_rec(root, prefix, results):
    if root.isWordEnd:
        results.append(prefix)
    for i in range(ALPHABET_SIZE):
        if root.children[i]:
            char = chr(ord('a') + i) if i < 26 else str(i - 26)
            suggestions_rec(root.children[i], prefix + char, results)

def get_suggestions(root, query, limit=10):
    pCrawl = root
    query = query.lower()
    for c in query:
        index = char_to_index(c)
        if index is None or not pCrawl.children[index]:
            return []
        pCrawl = pCrawl.children[index]
    results = []
    suggestions_rec(pCrawl, query, results)
    return results[:limit]

def load_data(trie_root, category):
    files = {"Movies": "movies.txt", "Music": "music.txt", "Departments": "departments.txt"}
    file_path = files.get(category, "movies.txt")
    try:
        with open(file_path, "r") as file:
            for line in file:
                insert(trie_root, line.strip())
    except FileNotFoundError:
        st.error(f"Error: {file_path} not found.")

# Initialize Streamlit interface
def main():
    st.set_page_config(layout="wide", page_title="Search Engine", initial_sidebar_state="expanded")
    st.title("Enhanced Search Engine")

    # Sidebar for category selection
    category = st.sidebar.selectbox("Select a Category", ["Movies", "Music"])

    # User Preferences
    num_suggestions = st.sidebar.slider("Number of Suggestions to Display", 1, 20, 10)
    dark_mode = st.sidebar.checkbox("Enable Dark Mode")

    # Initialize Trie root
    trie_root = get_node()
    load_data(trie_root, category)

    # Search bar for queries
    query = st.text_input("Enter search query", "")

    # Session state for history and bookmarks
    if "history" not in st.session_state:
        st.session_state.history = []
    if "bookmarks" not in st.session_state:
        st.session_state.bookmarks = []

    # Dark mode CSS
    if dark_mode:
        st.markdown("""
        <style>
        body {
            background-color: #111111;
            color: #eeeeee;
        }
        </style>
        """, unsafe_allow_html=True)

    # Show real-time suggestions
    if query:
        suggestions = get_suggestions(trie_root, query, num_suggestions)
        st.write(f"Found {len(suggestions)} suggestions:")
        for suggestion in suggestions:
            st.write(suggestion)

    # Search button
    if st.button("Perform Search"):
        start_time = time.time()
        suggestions = get_suggestions(trie_root, query, num_suggestions)
        end_time = time.time()

        search_time = end_time - start_time
        st.write(f"Search completed in {search_time:.4f} seconds")

        if suggestions:
            st.write("Suggestions found:")
            for suggestion in suggestions:
                st.write(suggestion)
        else:
            st.write("No results found.")

        # Log search history with timestamp
        with open("search_history.txt", "a") as file:
            file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{query},{'|'.join(suggestions)}\n")


    # Bookmark current query
    if st.button("Bookmark Query"):
        if query:
            st.session_state.bookmarks.append(query)
            st.success("Query bookmarked!")

    if st.button("View Search History"):
        try:
            with open("search_history.txt", "r") as file:
                history = file.readlines()
            if history:
                st.write("Search History:")
                for entry in history:
                    parts = entry.strip().split(",", maxsplit=2)
                    if len(parts) == 3:
                        timestamp, query, suggestions = parts
                        suggestions_list = suggestions.split('|') if suggestions else []
                        st.write(f"- **{timestamp}**: `{query}` -> Suggestions: {suggestions_list}")
                    elif len(parts) == 2:
                        timestamp, query = parts
                        st.write(f"- **{timestamp}**: `{query}` -> Suggestions: None")
                    else:
                        st.write(f"- Invalid entry: {entry.strip()}")
            else:
                st.write("No search history available.")
        except FileNotFoundError:
            st.write("No search history file found.")


    # Export search history
    if st.button("Export Search History"):
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Search History", csv, "search_history.csv", "text/csv")
        else:
            st.write("No search history available.")

    # View bookmarks
    if st.button("View Bookmarks"):
        if st.session_state.bookmarks:
            st.write("Bookmarked Queries:")
            for bookmark in st.session_state.bookmarks:
                st.write(f"- {bookmark}")
        else:
            st.write("No bookmarks available.")

    # Advanced analytics
    if st.button("View Search Analytics"):
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            st.write(f"Total searches: {len(df)}")
            st.write("Most frequent queries:")
            st.write(df['query'].value_counts())

            # Plot query trends
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            plt.hist(df['hour'], bins=24, color='skyblue', alpha=0.7)
            plt.title("Search Trends by Hour")
            plt.xlabel("Hour of Day")
            plt.ylabel("Number of Searches")
            st.pyplot(plt.gcf())
        else:
            st.write("No search data to analyze.")

if __name__ == "__main__":
    main()

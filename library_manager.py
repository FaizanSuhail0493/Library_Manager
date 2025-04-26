import streamlit as st
import pandas as pd
import json
import requests
import os
import time
import datetime as dt
import random
import ploty.express as px
import plotty.graph_objects as go
from streamlit_lottie import st_lottie

#set page confirguration
st.set_page_config(
    page_title="Library Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

#custom css for styling
st.markdown("""
<style>
    .main-header {
        color: #f63366;
        font-size: 3rem !important;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        font-family: 'Times New Roman', Times, serif;
    }
    .sub-header {
        color: #f63366;
        font-size: 1.8rem !important;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
        font-family: 'Times New Roman', Times, serif;
    }
    .success-message {
        padding: 1rem;
        background-color: #00ff00;
        border-left: 6px solid #00ff00;
        border-radius: 0.375rem;
        font-family: 'Times New Roman', Times, serif;
    }
    .warning-message {
        padding: 1rem;
        background-color: #ffcc00;
        border-left: 6px solid #ffcc00;
        border-radius: 0.375rem;
        font-family: 'Times New Roman', Times, serif;
    }
    .book-card {
        padding: 1rem;
        background-color: #f9f9f9;
        border: 1px solid #e6e6e6;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
        font-family: 'Times New Roman', Times, serif;
    }
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .read-badge {
        background-color: #00ff00;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .unread-badge {
        background-color: #ff0000;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .action-button {
        margin-right: 0.5rem;
    }
    .stButton>button {
        border-radius: 0.375rem;
    }
</style>
""", unsafe_allow_html=True)


def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

#load the library

def load_library():
    try:
        if os.path.exists("library.json"):
            with open("library.json", "r") as file:
                st.session_state.library = json.load(file)
            return True
        return False
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return False
    

#save the library
def save_library():
    try:
        with open("library.json", "w") as file:
            json.dump(st.session_state.library, file, indent=4)
        return True
    except Exception as e:
        st.error(f"Error in Saving Library: {str(e)}")
        return False

#add a book to the library

def add_book_to_library(title, author, publication_year, genre, read_status):
    book = {
        "title": title,
        "author": author,
        "publication_year": publication_year,
        "genre": genre,
        "read_status": read_status,
        "date_added": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    st.session_state.book_added = True
    time.sleep(0.5) #added a delay to show the success message

#remove a book from the library

def remove_book_from_library(index):
    if 0 <= index < len(st.session_state.library):
       del st.session_state.library[index]
       save_library()
       st.session_state.book_removed = True
       return True
    return False

#search for a book in the library

def search_books(search_term, search_by):
    search_term = search_term.lower()
    results = []

    for book in st.session_state.library:
        if search_by == "Title" and search_term in book["title"].lower():
            results.append(book)
        elif search_by == "Author" and search_term in book["author"].lower():
            results.append(book)
        elif search_by == "Genre" and search_term in book["genre"].lower():
            results.append(book)
    st.session_state.search_results = results

#Calculate Library stats
def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book["read_status"] == "Read")
    percent_read = (read_books / total_books) * 100 if total_books > 0 else 0

    genres = {}
    authors = {}
    decades = {}

    for book in st.session_state.library:
        if book['genre'] in genres:
            genres[book['genre']] += 1
        else:
            genres[book['genre']] = 1
        
        #count Author
        if book['author'] in authors:
            authors[book['author']] += 1
        else:
            authors[book['author']] = 1

        #count Decades
        decade = (book['publication_year']// 10) * 10
        if decade in decades:
            decades[decade] += 1
        else:
            decades[decade] = 1
    
    #sort by count
    genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
    decades = dict(sorted(decades.items(), key=lambda x: x[0]))

    return {
        'total Books': total_books,
        'read Books': read_books,
        'percent Read': percent_read,
        'genres': genres,
        'authors': authors,
        'decades': decades
    }

#Visualize Library Stats
def create_visualizations(stats):
    if stats['total_books'] > 0:
        #Genre Distribution
        fig_read_status = go.Figure(data=[go.Pie(
            labels=["Read", "Unread"],
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            hole=4,
            marker_colors=['#00ff00', '#ff0000']
        )])

        fig_read_status.update_layout(
            title_text = "Read vs Unread Books",
            showlegend = True,
            height = 400
        )
        st.plotly_chart(fig_read_status, use_container_width=True)

    #Bar chart for Genre Distribution
    if stats['genres']:
        genres_df = pd.DataFrame({
            'Genre': list(stats['genres'].keys()),
            'Count': list(stats['genres'].values())
        })
        fig_genres = px.bar(
            genres_df,
            x='Genre',
            y='Count',
            color='Count',
            color_continuous_scale=px.colors.sequential.Viridis.Blues
        )
        fig_genres.update_layout(
            title_text = "Book  by Publication Decade",
            xaxis_title = "Decade",
            yaxis_title = "Number of Books",
            height = 400
        )
        st.plotly_chart(fig_genres, use_container_width=True)
    if stats['decades']:
        decades_df = pd.DataFrame({
            'Decade': (f"{decade}s" for decade in stats['decades'].keys()),
            'Count': list(stats['decades'].values())
        })
        fig_decades = px.line(
            decades_df,
            x='Decade',
            y='Count',
            markers=True,
            line_shape='spline'
        )
        fig_decades.update_layout(
            title_text = "Book by Publication Decade",
            xaxis_title = "Decade",
            yaxis_title = "Number of Books",
            height = 400
        )
        st.plotly_chart(fig_decades, use_container_width=True)

    #Load Library
load_library()
st.sidebar.markdown("<h1 style='text-align: center;'> Navigation </h1>", unsafe_allow_html=True)
lottie_book = load_lottieurl("https://assets9.lottiefiles.com/temp/lf20_2jzj3e.json")
if lottie_book:
    with st.sidebar:
        st_lottie(lottie_book, height=200, key='book_animation')

nav_options = st.sidebar.radio(
    "Choose an Option",
    ["View Library", "Add Book", "Search Books", "Library Statics"])

if nav_options == "View Library":
    st.session_state.current_view = "library"
elif nav_options == "Add Book":
    st.session_state.current_view = "add_book"
elif nav_options == "Search Books":
    st.session_state.current_view = "search_books"
elif nav_options == "Library Statics":
    st.session_state.current_view = "stats"

st.markdown("<h1 class='main-header'>Library Manager</h1>", unsafe_allow_html=True)
if st.session_state.current_view == "add":
    st.markdown("<h2 class='sub-header'>Add a New Book</h2>", unsafe_allow_html=True)

    #adding book input form
    with st.form(key='add_book_form'):
        col1, col2 = st.columns(2)

    with col1:
        title = st.text_input("Book Title", max_chars=100)
        author = st.text_input("Author", max_chars=100)
        publication_year = st.number_input("Publication Year", min_value=1900, max_value=dt.datetime.now().year, step=1, value=2023)
        
    with col2:
        genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science Fiction", "Fantasy", "Mystery", "Biography", "History", "Romance"])
        read_status = st.selectbox("Read Status", ["Read", "Unread"], horizontal=True)
        read_bool = read_status == "Read"
    submit_button = st.form_submit_button(label='Add Book')

    if submit_button and title and author:
        add_book_to_library(title, author, publication_year, genre, read_bool)
           
if st.session_state.book_added:
    st.markdown("<div class='success-message'>Book added successfully!</div>", unsafe_allow_html=True)
    st.session_state.book_added = False

elif st.session_state.current_view == "library":
    st.markdown("<h2 class='sub-header'>Your Library</h2>", unsafe_allow_html=True)

    if not st.session_state.library:
        st.warning("<div class: 'Warning Message'> Your library is empty. Add some books!</div>", unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i, book in enumerate(st.session_state.library):
            with cols[i % 2]:
                st.markdown(f"""<div class='book-card'>
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    <p><strong>Date Added:</strong> {book['date_added']}</p>
                    <span class='{'read-badge' if book['read_status'] else 'unread-badge'}'>{'Read' if book['read_status'] else 'Unread'}</span>
                    </div>
""", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Remove Book", key=f"remove_{i}", use_container_width=True):
                        if remove_book_from_library(i):
                            st.rerun()
                with col2:
                    new_status = not book['read_status']
                    status_label = "Mark as read" if new_status else "Mark as Unread"
                    if st.button(status_label, key=f"status_{i}", use_container_width=True):
                        st.session_state.library[i]['read_status'] = new_status
                        save_library()
                        st.rerun()
        
        if st.session_state.book_removed:
            st.markdown("<div class='success-message'>Book removed successfully!</div>", unsafe_allow_html=True)
            st.session_state.book_removed = False
        elif st.session_state.current_view == "search_books":
            st.markdown("<h2 class='sub-header'>Search Books</h2>", unsafe_allow_html=True)

            search_by = st.selectbox("Search By", ["Title", "Author", "Genre"])
            search_term = st.text_input("Search Term", max_chars=100)

            if st.button("Search" use_container_width=True):
                if search_term:
                    with st.spinner("Searching..."):
                        time.sleep(1)
                        search_books(search_term, search_by)
            if hasattr(st.session.state, 'search_results'):
                if st.session_state.search_results:
                    st.markdown(f"<h3> Found {len(st.session.state.search_results)} result:</h3>", unsafe_allow_html=True)

                    for i, book in enumerate(st.session_state.search_results):
                        st.markdown(f"""<div class='book-card'>
                            <h3>{book['title']}</h3>
                            <p><strong>Author:</strong> {book['author']}</p>
                            <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                            <p><strong>Genre:</strong> {book['genre']}</p>
                            <p><strong>Date Added:</strong> {book['date_added']}</p>
                            <span class='{'read-badge' if book['read_status'] else 'unread-badge'}'>{'Read' if book['read_status'] else 'Unread'}</span>
                            </div>
""", unsafe_allow_html=True)
        elif search_term:
            st.markdown("<div class='warning-message'>No results found.</div>", unsafe_allow_html=True)
elif st.session_state.current_view == "stats":
    st.markdown("<h2 class='sub-header'>Library Statistics</h2>", unsafe_allow_html=True)

    if not st.session_state.library:
        st.warning("<div class: 'Warning Message'> Your library is empty. Add some books!</div>", unsafe_allow_html=True)
    else:
        stats = get_library_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Books", stats['total Books'])
        with col2:
            st.metric("Read Books", stats['read Books'])
        with col3:
            st.metric("Percent Read", f"{stats['percent Read']:.1f}%")
        create_visualizations()

        if stats['authors']:
            st.markdown("<h3>Top Authors</h3>", unsafe_allow_html=True)
            top_authors = dict(list(stats['authors'].items())[:5])
            for author, count in top_authors.items():
                st.markdown(f"**{author}**: {count} book{'s' if count > 1 else ''}")
st.markdown("---")
st.markdown("copyright © 2025 Library Manager. All rights reserved.", unsafe_allow_html=True)

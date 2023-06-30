from flask import Flask, render_template, request
import pickle
import pandas as pd
import requests

similarity = pickle.load(open('Hollywood_similarity.pkl', 'rb'))
movies = pickle.load(open('Hollywood_movies_list.pkl', 'rb'))

cosine_sim = pickle.load(open('bollywood_movie_similarity.pkl', 'rb'))
moviesDF = pickle.load(open('bollywood_movie_moviesDF.pkl', 'rb'))
indices = pickle.load(open('bollywood_movie_indices.pkl', 'rb'))
soupDF = pickle.load(open('bollywood_movie_soupDF.pkl', 'rb'))

movie_list = movies['title'].values

def get_poster(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=225f602acfc8d5068c945e5641942bd4&language=en-US'.format(movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500" + data['poster_path']

# MOVIE RECOMMENDATION FUNCTION
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(get_poster(movie_id))

    return recommended_movie_names, recommended_movie_posters

def plot_based_recommender(title, df = soupDF, cosine_sim = cosine_sim, indices = indices):
  title = title.lower()

  try:
    idx = indices[title]
  except KeyError:
    print('Movie does not exist :(')
    return False
  
  bollywood_movie_names = []
  bollywood_movie_posters = []

  sim_scores = sorted(list(enumerate(cosine_sim[idx])), key = lambda x: x[1], reverse = True)

  for sim_scores in sim_scores[1:6]:
    bollywood_movie_names.append(df['name'].iloc[sim_scores[0]])
    hindi_movie_id = moviesDF['movie_id'].iloc[sim_scores[0]]
    bollywood_movie_posters.append(get_poster(hindi_movie_id))

  return bollywood_movie_names, bollywood_movie_posters

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/', methods=['POST'])
def getval():
    movie_name = request.form['Name']
    categ = request.form['Categ']
    if categ == "Hollywood" or categ == "hollywood":
        recommendations, posters = recommend(movie_name)
    if categ == "Bollywood" or categ == "bollywood":
        recommendations, posters = plot_based_recommender(movie_name)
    og_name = movie_name

    return render_template('results.html', name = recommendations, poster = posters, original_name = og_name)

if __name__ == "__main__":
    app.run()




   
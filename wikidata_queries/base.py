import urllib.request
# https://stackoverflow.com/questions/30755625/urlerror-with-sparqlwrapper-at-sparql-query-convert
# #if the arg is empty in ProxyHandler, urllib will find itself your proxy config.
# proxy_support = urllib.request.ProxyHandler({})
# opener = urllib.request.build_opener(proxy_support)
# urllib.request.install_opener(opener)
from typing import List, NamedTuple, Tuple


from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

from wikidata_queries.contracts import ContentRatingContract, FilmContract
from wikidata_queries.queries import CR_QUERY_TEMPLATE, SINGLE_PROP_FILM_QUERY_TEMPLATE, WIKIDATA_ID_FROM_IMDB_ID_QUERY, \
    PREQUEL_SEQUEL_BY_WIKIDATA_ID_QUERY


class WikiDataQueryBuilder:
    def __init__(self):
        self.sparql_builder = SPARQLWrapper("https://query.wikidata.org/sparql",
                                            agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")

    def raw_query(self, fields: List[str], raw: str):
        self.sparql_builder.setQuery(raw)
        self.sparql_builder.setReturnFormat(JSON)
        results = self.sparql_builder.query().convert()
        results_df = pd.json_normalize(results['results']['bindings'])
        results_df = results_df[[f'{field}.value' for field in fields]]
        return results_df

    def query(self, fields: List[str], where: str, limit: int = None) -> pd.DataFrame:
        # From https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples#Cats
        fields_p = " ".join([f'?{field}' for field in fields])
        query = f"""
           SELECT {fields_p}
           WHERE
           {{
             {where}
           }}
           """
        self.sparql_builder.setQuery(query)
        if limit:
            query += f"""
            LIMIT {limit}
            """
        self.sparql_builder.setReturnFormat(JSON)
        results = self.sparql_builder.query().convert()

        results_df = pd.json_normalize(results['results']['bindings'])
        results_df[[f'{field}.value' for field in fields]].head()
        return results_df


builder = WikiDataQueryBuilder()


def get_individual_id_from_url(entity_url: str) -> str:
    return entity_url.replace('http://www.wikidata.org/entity/', '')


def get_content_ratings_for_film(wikidata_id: str) -> List[ContentRatingContract]:
    query = CR_QUERY_TEMPLATE
    df = builder.raw_query(['crpLabel', 'countryLabel', 'contentRatingLabel'], query.format(film=wikidata_id))
    ratings: List[ContentRatingContract] = []
    for index, row in df.iterrows():
        label = row['crpLabel.value']
        country = row['countryLabel.value']
        rating_category = row['contentRatingLabel.value']
        ratings.append(ContentRatingContract(label=label, appliesInCountry=country, value=rating_category))
    return ratings


def get_single_valued_prop(wikidata_id: str) -> FilmContract:
    query = SINGLE_PROP_FILM_QUERY_TEMPLATE
    df = builder.raw_query(['originatingCountryLabel', 'originalLangLabel', 'publicationDateLabel'], query.format(film=wikidata_id))
    for index, row in df.iterrows():
        country = row['originatingCountryLabel.value']
        lang = row['originalLangLabel.value']
        pub_date = row['publicationDateLabel.value']
        return FilmContract(hasCountryOfOrigin=country, hasOriginalLanguage=lang, hasPublicationDate=pub_date)


def get_prequel_sequel(wikidata_id: str) -> Tuple[FilmContract]:
    query = PREQUEL_SEQUEL_BY_WIKIDATA_ID_QUERY
    df = builder.raw_query(['prequels', 'sequels'], query.format(wikidata_id=wikidata_id))
    row = df.iloc[0]
    prequels = tuple(map(lambda x: FilmContract(wikidata_id=get_individual_id_from_url(x), isPrequel=True),
                   row['prequels.value'].split(",")))
    sequels = tuple(map(lambda x: FilmContract(wikidata_id=get_individual_id_from_url(x), isSequel=True),
                  row['sequels.value'].split(",")))
    return prequels + sequels


def get_from_imdb_id(imdb_id: str) -> str:
    """

    Args:
        imdb_id:

    Returns: The wikidata id of the given movie with the given imdb id

    """
    df = builder.raw_query(['film'], WIKIDATA_ID_FROM_IMDB_ID_QUERY.format(imdb_id=imdb_id))
    return get_individual_id_from_url(df.iloc[0]['film.value'])


class Genre(NamedTuple):
    wikidata_id: str
    label: str


class GenreWithSub(NamedTuple):
    genre: Genre
    subgenre: Genre


def get_genre_with_subgenres() -> List[GenreWithSub]:
    query = """
    SELECT ?genre ?genreLabel ?subGenre ?subGenreLabel
    {
      ?subGenre wdt:P31 wd:Q201658;
             wdt:P279 ?genre.
      ?genre wdt:P31 wd:Q201658
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en,[AUTO_LANGUAGE]".}
    }
    """.strip()
    df = builder.raw_query(['genre', 'genreLabel', 'subGenre', 'subGenreLabel'], query)
    lst: List[GenreWithSub] = []
    for index, row in df.iterrows():
        genre = row['genre.value']
        genrelabel = row['genreLabel.value']
        subgenre = row['subGenre.value']
        subgenrelabel = row['subGenreLabel.value']
        lst.append(GenreWithSub(
            genre=Genre(wikidata_id=get_individual_id_from_url(genre), label=genrelabel),
            subgenre=Genre(wikidata_id=get_individual_id_from_url(subgenre), label=subgenrelabel)
        ))
    return lst


def main():
    print(get_single_valued_prop('Q61448040'))


if __name__ == '__main__':
    main()

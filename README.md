Elastic Semantic Search
==============================

This project is a poc for semantic search infra with `Elasticsearch`. The steps to use the semantic search encompasses building a vectorized embeddings of the original documents and the query and then finding the similarities / matches between the query and the documents. In this system, we are interested to build a high throughput and performant search system.

Before starting with this poc, visit [DEVGUIDE](DEVGUIDE.md) to setup the devtools for python environment and the `Elasticsearch` cluster. We used docker installation of `Elasticsearch` in this project.


Quick Start
------------------
Main commands are in `Makefile`. Here are the steps to use them to make index, embed documents' vectors and then a cli to make searches.

1. Create new index format in ES:
```python
make index
```

2. Index sample documents in ES with embeddings:
```python
make embedding
```

3. Test search results with cli:

```python
make search
```

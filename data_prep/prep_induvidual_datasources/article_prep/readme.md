## What does this folder do?
This folder contains code to retrieve articles from directus (given their slug). This is done in `./retrieve.py`
After retrieval, all the articles are conveted into JSON and stored in seperate files inside `./formatted_articles/`. This is also done by `./retrieve.py`
Then, `./combined_articles.py` will read each file inside `./formatted_articles/`, combine their contents, and convert them into XML format and store it in `./combined_articles.xml`:

```
<all docs>
	<document>
		<slug>
		article-1-slug
		</slug>
		<content>
		article 1 content
		<content>
	</document>
	<document>
		<slug>
		article-2-slug
		</slug>
		<content>
		article 2 content
		<content>
	</document>
</all docs>
```
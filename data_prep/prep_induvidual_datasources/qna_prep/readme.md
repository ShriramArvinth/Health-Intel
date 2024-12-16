## What does this folder do?
This folder contains code to retrieve articles from directus (given their slug). This is done in `./retrieve.py`
After retrieval, all the articles are conveted into JSON and stored in seperate files inside `./formatted_qna/`. This is also done by `./retrieve.py`. Then, `./combined_qna.py` will read each file inside `./formatted_qna/`, combine their contents, and convert them into XML format and store it in `./combined_qna.xml`:

```
<all docs>
	<document>
		<slug>
		qna-1-slug
		</slug>
		<content>
		qna 1 content
		<content>
	</document>
	<document>
		<slug>
		qna-2-slug
		</slug>
		<content>
		qna 2 content
		<content>
	</document>
</all docs>
```
# Wikiracing
A Wikirace is a race between any number of participants, using links to travel from one Wikipedia page to another.  -Wikipedia

## My Solution
Work smarter not harder:   
- Flask: API endpoint to kick off game
- Spacy: NLP engine computes word similarity scores by comparing word vectors
- Celery: Celery creates tasks which are sent to workers who listen to distinct queues for work. There is also availability for parallel processing through increasing the number of workers. 
- Redis: A fast caching database also used by celery.   
   
![Architecture Diagram](/images/architecture_diagram.png)  
   
All previous solutions found online rely on breadth first search to look through all the links on Wikipedia with no prior context. Instead of searching blindly with no context, use a natural language processing engine to seek out pages with high similarity scores with respect to the goal end page and visit those pages first. Run the same search going from start page to end page both forwards and in reverse and meet somewhere in the middle. Distribute this work across multiple Celery workers to allow for parallel processing.  

## How to Run:
This depends on having Docker and Docker Compose installed and setup.   
Clone this repository and navigate to the folder then run:   
```
$ docker-compose up
```   
The first build may take a while because it grabs the Spacy english mode for the first time which is quite large. This file is then cached for later runs.   
Using a browser or Postman or any client of your choice send a get request to:   
```
http://localhost:5001/find/[start page title]/[end page title]
```   
Navigate to Redis commander to monitor tasks and the status database:   
```
http://localhost:8081/
```   
When the search completes you can see the results and total time spent computing in the redis status db.   
Or you can issue the same get request again and instead of “Pending” it will respond with the traversed path to that page and time spent computing in seconds.

## How to test:
```
$ docker-compose -f docker-compose-tests.yml up
```

## Debugging:
- Redis commander: allows for monitoring of database and task queues   
	Navigate to:   
	```
	http://localhost:8081/
    ``` 
- Flower: web based tool for monitoring and administering Celery clusters   
	Start tasks you wish to debug with flower like so:   
	```
	$ docker-compose restart [task name or space separated task names] flower
    ```
    Navigate to:   
	```
	http://localhost:8888/
    ``` 
- Orphan containers: These can happen sometimes just kill them.   
    Run command:   
    ```
    $ docker-compose down --remove-orphans
    ```
  
## Benchmarks Achieved
- From Tennessee to Sloth:   
["Tennessee", "Evangelicalism", "Piety", "Gluttony", "Greed", "Panic", "William Beebe", "Sloth"]   
42.57 Seconds local run.
- From Mike Tyson to Potato:   
["Mike Tyson", "Donald Curry", "Marsala", "Poland", "Potato"]   
56.87 Seconds local run.

## Project Timeline
- Figure out how to integrate flask, celery, and redis inside a docker-compose (~2 Hours)
    - Accomplished first day following an example I found [here](https://github.com/mattkohl/docker-flask-celery-redis).
- Learn how to work with Media Wiki API to obtain links/linkshere (~30 Min)
    - Learned how to get links and linkshere from Media Wiki API first day.
- Develop algorithm in simple BFS (2-3 Days):
    - Get simple algorithm working.
    - This includes designing making celery tasks and redis db to fit project needs.
- Look into Spacy similarity scoring (1-2 Hours)
    - Follow example found [here](https://www.geeksforgeeks.org/python-word-similarity-using-spacy/).
    - Reference [Spacy API on Similarity](https://spacy.io/usage/vectors-similarity).
    - Plugged Spacy into algorithm to sort links based on highest similarity score with respsect to goal end path.
- Re-designing algorithm to work with callback to accomplish DFS (1-2 Days)
    - Due to the fact that links are sorted we switch to DFS.
    - Why DFS: We want to always travel down the most probable path (path's with highest similarity scores).
    - Attempted to design algorithm to only search down a path if the score improves if not then jump to next link in DFS tree.
- Give find and nlp celery tasks distinct queues granting them different sets of workers (1 Day)
    - NLP does a lot of work and it needs its own set of workers separate from find which also does lots of work.
- Build python Classes around redis db interactions for tracking history and status (1 Day)
    - Done to ensure consistent reading and writing of data prevents errors.
    - Makes code easier.
- Scrap previous algorithm, build improved wiki racer search (1-2 Days)
    - Take advantage of Redis build in sorted sets data type to store pages in order of similarity score.
    - Learn the traversed path taken to discover each new page and store in db.
    - Allows for searching based on highest scoring page in each round (because each page has a discover traversed path).
- Testing (3 Days)
    - Mocking flask, celery, and redis made this very difficult and time consuming.
    - Ensuring tests had access to directories they were testing within docker-compose.
    - building tests their own docker compose.
- Documenting (2 Days)
    - Create README.
    - Create Omnigraffle architecture diagram.
- Last day: Branch off and work on improved algorithm (1 Day)
    - Update search to go both forward and backward:
        - Forward search based on links.
        - Backward search based on links-here.
        - Search to see if there is any intersections in pages found from both forward and reversed search upon discovery of new links.
        - If intersection found build a solution path from the intersection points traversed paths.
    - Add in tests for new algorithm.
    - Test all weird edge cases.
    - Update README.
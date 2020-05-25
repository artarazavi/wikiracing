# Wikiracing
A Wikiraceis a race between any number of participants, using links to travel from one Wikipedia page to another.  -Wikipedia

## My Solution
Work smarter not harder:   
- Flask: API endpoint to kick off game
- Spacy: NLP engine computes word similarity scores by comparing word vectors
- Celery: Celery creates tasks which are sent to workers who listen to distinct queues for work. There is also availability for parallel processing through increasing the number of workers. 
- Redis: A fast caching database also used by celery.   
   
![Architecture Diagram](/images/architecture_diagram.png)  
   
All previous solutions found online rely on breadth first search to look through all the links on Wikipedia with no prior context. Instead of searching blindly with no context, use a natural language processing engine to seek out pages with high similarity scores with respect to the goal end page and visit those pages first. Distribute this work across multiple Celery workers to allow for parallel processing.  

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
Or you can issue the same get request again and instead of “Pending” it will respond with the traversed path to that page.

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
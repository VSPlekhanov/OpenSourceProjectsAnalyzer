# OpenSourceProjectsAnalyzer
In order to run the application go to the project root folder and execute
```
docker build -t os-analyzer .
```
And then
```
docker run -p 4200:4200 -p 8080:8080 os-analyzer
```
Then after it starts go to the http://localhost:4200/search
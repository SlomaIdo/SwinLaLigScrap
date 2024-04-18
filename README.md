# SwinLaLigScrap
I plan to scrap a website with swimming results 

This project is all about getting all of the resuts from the swimming contest web page, push to a database and preform some EDA. 

The Main building blocks of this project are:
1. Running a scraper on the web site to get all of the results in csv local files. 
2. Pushing all results to SQLite Database
3. Preforming a EDA and queries on top of the database. 

The secondary objectives:
1. Running all python. If I can, I won't use R at all, especilly on the analysis party (can't promide)
2. Use the pipeline to run, eveytime new data is uploaded. 
3. Use good practices. 

## Web Scrapping

Here are what I found on the web site:
-   Everything is scrapable. I was able to get data from high level till the very last results. Some of the data, is in hebrew. 
-   The web site is build wth ASP framwork, meaning I will not get all of the dara on the HTML. 

### Scrape strucutre
-   The main site is: `https://isr.org.il/competitions.asp`. On this page I am finding a table with all of the competitions that are between this and that range. For example: 
In order to find all of the __swimming__ competitions that finished between 2023-2024, I should log into:
`https://isr.org.il/competitions.asp?cYear=2024&cMonth=0&cType=1&cMode=0&isFinish=true`
Where type `1` is for swimming. The rest is really stright forward, I belive.

There is another value: "Past competitions", these are competitions from the past and the year should be = `2000`.

-   Once we got the year and competitions, we should map the year--->competition ID relationship. These should be the first hirarcey we loop over.

#### Competition List Mapping
For every page we are retriving via the links, we can extract all of the competitions and thier links. This can be done since all competitions are in this format:
`<td class="rr c-name"><a href="comp.asp?compID=456" tabindex="26">תחרות אזורית צפון קרית ביאליק 1</a></td>`

The link can be added to the main link so we can move one step down and extract information per competition. 
for example: `https://isr.org.il/comp.asp?compID=454`

#### Scrapping a single competition

We can enter each Competition and look for the heats that were played during that day. 
Apperantly, The heats data is stored in a AthleticsDiscipline object that can be fetched from the loglig server, which is the provider of this service. 
For example: `https://loglig.com:2053/LeagueTable/AthleticsDisciplines/9816`

So all we need to get from here is to find the `iframes` that are connected to the competition batch. This will connect us to the days. 
Also we should collect info from the meta data. 
TODO: What is the meta data for each competition?

#### AthleticsDisciplines
AthleticsDisciplines is the main container for a day of a competition.
Each AthleticsDisciplines starts with a table with those column:
# Web Scraping Demo

This project is intended as a demo for developing a python web scraping application

## Overview

The script relies on beautiful soup and python requests to query the first 200 pages of the amazon results for gaming monitors. It then filters the targetted elements to remove non monitors. It publishes the results to an excel file and also a psql database hosted on AWS.
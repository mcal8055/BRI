# Load necessary library
library(dplyr)
library(lubridate)

# File paths
avalanches_file <- "Data/Avalanches/avalanches.csv"
observations_file <- "Data/Observations/observation-export-2.csv"
forecasts_file <- "Scrapers/data/forecast_data.csv"

# Read in CSV files
avalanches_df <- read.csv(avalanches_file, stringsAsFactors = FALSE)
observations_df <- read.csv(observations_file, stringsAsFactors = FALSE)
forecasts_df <- read.csv(forecasts_file, stringsAsFactors = FALSE)

#clean and standardize data
cleansed_avalanches_df <- avalanches_df |>
   select(avalanche_aspect = Aspect, avalanche_date = Date, Region, weakLayer = "Weak.Layer"
, Place, Caught, Carried, buriedPartly = 'Buried...Partly', buriedFully = 'Buried...Fully', Injured, Killed)
cleansed_observations_df <- observations_df |>
  select(observation_aspect = aspect, observation_date = date, elevation, primaryAvalancheProblem, region)
cleansed_forecasts_df <- forecasts_df |>
  select(forecast_id, forecast_date = date, Problem1 = 'Avalanche.Problem..1', Problem2 = 'Avalanche.Problem..2', Problem3 = 'Avalanche.Problem..3',
         Problem4 = 'Avalanche.Problem..4', Problem5 = 'Avalanche.Problem..5')




# Avalanche Advisor

This project is an in-progress pipeline to analyze historical avalanche forecast data from the Utah Avalanche Center (UAC) and model accident outcomes based on forecasted risk factors. Due to the lack of a public API, a custom web scraper was developed to retrieve and structure this information.

## Project Goals

- Collect, clean, and standardize historical avalanche forecast data
- Build a reproducible modeling pipeline to estimate avalanche-related accident outcomes
- Perform exploratory data analysis and evaluate predictive models
- Extend modeling with terrain-specific risk features from image-based data (planned)

## Current Status

- ✅ **Web scraping**: Python script using `selenium` to retrieve structured forecast data from the UAC website
- ✅ **Data integration**: `Forecaster.R` file ingests and cleans forecast, observation, and avalanche report CSVs
- 🚧 **Modeling pipeline**: Logistic regression models in development using `caret` (R)
- 🚧 **Exploratory analysis**: To be conducted as part of MVP
- 📝 **Image segmentation**: Planned feature to extract terrain-level avalanche risk variables from forecast images

## Tech Stack

- **Python**: `selenium`, `pandas` (web scraping)
- **R**: `tidyverse`, `caret` (data processing and modeling)

## To-Do for MVP

- Perform exploratory data analysis (EDA) on cleaned datasets
- Evaluate logistic regression and alternative models for predicting accident outcomes

## Planned Features

- Train image segmentation model using `cv2` (Python) to extract:
  - Avalanche risk by elevation and aspect
  - Avalanche likelihood and size estimates
- Integrate image-derived variables as independent features into model pipeline

## Motivation

Avalanche danger is spatially and temporally dynamic. This project aims to unify textual, tabular, and visual forecast data into a cohesive pipeline that supports accident risk modeling at the terrain level, contributing to more data-informed decision-making in backcountry safety.

---

*This project is under active development. Contributions and feedback are welcome as we move toward a minimum viable product (MVP) and beyond.*

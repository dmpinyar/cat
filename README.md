# cat
An end-to-end machine learning pipeline to analyze horse racing statistics and forecast race outcomes.
Converted an old Windows desktop into an Ubuntu server, configured with SSH access and Tailscale VPN, to act as a remote computational environment for running algorithms without consuming local laptop resources.
Developed a web scraping framework using Selenium WebDriver to systematically navigate and extract data from a multi-page horse racing results website.
Optimized scraping with concurrent.futures multithreading, reducing runtime by parallelizing requests across multiple threads.
Structured large-scale racing datasets into NumPy arrays for efficient storage and computation, enabling fast downstream analysis.
Developed and evaluated a PyTorch ML model with MSE Loss and RMSprop, leveraging preprocessing and feature engineering to accurately predict outcomes from historical race data.

omitted saved-data directory, but all used scripts are here

Currently lacking a real UI, if I revisit this project and develop it past simple practice I'll build something in the main function to where I don't have to manually write in functions.

Lacking storage of ML weights. Something I should probably work on.

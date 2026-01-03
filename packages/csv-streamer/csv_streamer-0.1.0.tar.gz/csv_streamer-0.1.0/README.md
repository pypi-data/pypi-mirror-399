# CSV Streamer

I find myself doing a lot of the same thing recently... and that thing is streaming large csv files over the network in batches. 

So I made a small python library using a few techniques that I know to stream csv files and yield them as batches of arrow tables for further processing/wrangling etc.

There's 4 paths and one entry point:

- stream_csv()

You can stream:

- Local CSVs
- Local CSVs in a zip file
- Remote CSVs
- Remove CSVs in a zip file

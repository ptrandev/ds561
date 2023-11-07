from google.cloud import storage
import numpy as np
from tqdm import tqdm
import concurrent.futures
import os
from argparse import ArgumentParser
import re


def calculate_statistics(outlinks):
    inlinks = outlinks.transpose()

    print()

    # calculate statistics
    print("Outlinks")
    print("---")
    print(f"Average number of outlinks: {np.mean(np.sum(outlinks, axis=1))}")
    print(f"Median number of outlinks: {np.median(np.sum(outlinks, axis=1))}")
    print(f"Max number of outlinks: {np.max(np.sum(outlinks, axis=1))}")
    print(f"Min number of outlinks: {np.min(np.sum(outlinks, axis=1))}")
    print(
        f"Quintiles: {np.quantile(np.sum(outlinks, axis=1), [0.2, 0.4, 0.6, 0.8, 1])}"
    )

    print()

    print("Inlinks")
    print("---")
    print(f"Average number of inlinks: {np.mean(np.sum(inlinks, axis=1))}")
    print(f"Median number of inlinks: {np.median(np.sum(inlinks, axis=1))}")
    print(f"Max number of inlinks: {np.max(np.sum(inlinks, axis=1))}")
    print(f"Min number of inlinks: {np.min(np.sum(inlinks, axis=1))}")
    print(f"Quintiles: {np.quantile(np.sum(inlinks, axis=1), [0.2, 0.4, 0.6, 0.8, 1])}")

    # print top 5 pages with most inlinks
    print()
    print("Top 5 pages with most inlinks:")
    print("---")
    top_5 = sorted(range(len(np.sum(inlinks, axis=1))), key=lambda i: np.sum(inlinks, axis=1)[i], reverse=True)[:5]

    # print top 5 pages with most outlinks
    print()
    print("Top 5 pages with most outlinks:")
    print("---")
    top_5 = sorted(range(len(np.sum(outlinks, axis=1))), key=lambda i: np.sum(outlinks, axis=1)[i], reverse=True)[:5]

    for page in top_5:
        print(f"Page {page}: {np.sum(outlinks, axis=1)[page]}")


def main():
    parser = ArgumentParser()

    parser.add_argument(
        "--d",
        type=float,
        default=0.85,
        help="The damping factor (default: 0.85)",
    )

    parser.add_argument(
        "--tol",
        type=float,
        default=0.005,
        help="The error tolerance (default: 0.005)",
    )

    parser.add_argument(
        "--bucket",
        type=str,
        default="ds561-ptrandev-hw02",
        help="The name of the Google Cloud Storage bucket (default: ds561-ptrandev-hw02)",
    )

    parser.add_argument(
        "--directory",
        type=str,
        default="html/",
        help="The directory path to the HTML files in the bucket (default: html/))",
    )

    parser.add_argument(
        "--num-threads",
        type=int,
        default=os.cpu_count() * 5,
        help="The number of threads to use for reading in the HTML files (default: os.cpu_count() * 5)",
    )

    args = parser.parse_args()

    # Create a storage client
    storage_client = storage.Client().create_anonymous_client()

    # Get a reference to the bucket
    bucket = storage_client.bucket(args.bucket)

    # Get a list of all the files in the directory
    blobs = bucket.list_blobs(prefix=args.directory)
    num_blobs = sum(1 for _ in bucket.list_blobs(prefix=args.directory))

    outlinks = np.zeros((num_blobs, num_blobs))

    # read in a blob and parse for outlinks
    def read_blob(blob):
        content = blob.download_as_string().decode("utf-8")

        # every blob's name is html/<filename>.html
        # get the file name as an integer
        filename = int(blob.name.split(".")[0].split("/")[1])

        # use regex to parse for <a> tags with href; if a link is 
        # <a HREF='1000.html'>1000</a>, then the regex should return 1000
        regex = re.compile(r'<a HREF="(\d+).html">')

        # parse the html
        links = re.findall(regex, content)

        # for each link, add an edge from the current page to the linked page
        for link in links:
            outlinks[filename, int(link)] = 1

    # multithreaded read in blobs; operate on each blob in parallel to create outlinks matrix
    def read_blobs():
        print()
        print(f"Spawning {args.num_threads} threads to read in blobs...")

        with tqdm(total=num_blobs) as pbar:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=args.num_threads
            ) as executor:
                futures = [executor.submit(read_blob, blob) for blob in blobs]

                for _ in concurrent.futures.as_completed(futures):
                    pbar.update(1)

    read_blobs()
    calculate_statistics(outlinks)

if __name__ == "__main__":
    main()

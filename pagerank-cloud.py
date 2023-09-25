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


def pagerank(A, d=0.85, tol=0.005):
    num_nodes = A.shape[0]
    prev_pagerank = np.zeros(num_nodes) / num_nodes
    error = 1.0

    incoming_edges = [np.where(A[:, i] == 1)[0] for i in range(num_nodes)]
    outgoing_edges = [A[i].sum(axis=1) for i in incoming_edges]

    while error > tol:
        current_pagerank = prev_pagerank.copy()

        # calculate pagerank for each node
        current_pagerank = (1 - d) + d * np.array(
            [
                np.sum(current_pagerank[incoming_edges[i]] / outgoing_edges[i])
                for i in range(num_nodes)
            ]
        )

        error = np.linalg.norm(current_pagerank - prev_pagerank)
        prev_pagerank = current_pagerank

    # normalize by the sum of pageranks
    prev_pagerank /= np.sum(prev_pagerank)

    return prev_pagerank


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

    # run pagerank and get the top 5 pages with highest page rank
    def run_pagerank():
        print()
        print("Running pagerank...")

        p = pagerank(outlinks, args.d, args.tol)

        # get the top 5 pages with highest page rank and their index
        top_5 = sorted(range(len(p)), key=lambda i: p[i], reverse=True)[:5]
        print("Top 5 pages with highest page rank:")
        print("---")
        for page in top_5:
            print(f"Page {page}: {p[page]}")

    read_blobs()
    calculate_statistics(outlinks)
    run_pagerank()

if __name__ == "__main__":
    main()

import sys
import json
from urllib import request




def clean_coverage_line(l):
    return l.split("\t")[-1].lstrip("coverage: ").rstrip("% of statements\n")

def POST(service_url, data):
    request_data = json.dumps(data).encode("utf-8")
    req  = request.Request(
        service_url,
        headers = {'content-type': 'application/json', 'encoding' : 'UTF-8'},
        data    = request_data
    )
    with request.urlopen(req) as response:
        if response.code == 200:
            print("Report properly sent")


if __name__ == "__main__":
    _, name, build_type, branch, report_address = sys.argv

    # Skip builds that are not cron jobs, this should be given by travis
    if build_type != "cron" or branch != "master":
        exit(0)

    average             = 0
    untested_modules    = 0
    tested_modules      = 0

    input_data = iter(sys.stdin)

    pipe = zip(input_data, input_data)

    for _, l in pipe:
        if "[no test files]" in l:
            untested_modules += 1
            continue
        average         += float(clean_coverage_line(l))
        tested_modules  += 1


    coverage_result = """Coverage report for {name}:
    {tested_modules} tested modules with an coverage average of {average:3.2f}%. {untested_modules} modules contain 0 tests. 
    """.format(
        name=name,
        average=average/tested_modules,
        tested_modules=tested_modules,
        untested_modules=untested_modules
    )

    POST(report_address, {"text": coverage_result})
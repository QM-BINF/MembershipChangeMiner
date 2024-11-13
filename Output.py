import csv
import io

def printCollabEventsToCSV(events, filename):
    writer = csv.writer(io.open(filename, 'w+', newline='', encoding="utf-8"), delimiter=";")
    writer.writerow(["Resource1", "Resource2", "Timestamp"])
    for event in events:
        tuple = event.getTupleFormat()
        writer.writerow([tuple[0].getLabel(), tuple[1].getLabel(), event.getEventTimestamp()])


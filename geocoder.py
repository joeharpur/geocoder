# Imports
from flask import Flask, render_template, request, Markup
import csv
import os


app = Flask(__name__)


SITE_ROOT = os.path.realpath(os.path.dirname(__file__))  # Site root directory
townlands_csv = os.path.join(SITE_ROOT, 'static/data', 'townlands.csv')  # Location of townlands csv
counties_csv = os.path.join(SITE_ROOT, 'static/data', 'counties.csv')  # Location of counties csv


def create_reference_dict(file):
    # Create reference dictionaries with X and Y coordinates mapped to place names
    with open(file, encoding='utf-8-sig') as csvfile:
        readcsv = csv.DictReader(csvfile)  # Read csv file as dictionary
        ref = {}
        # Building new dictionary with location names mapped to all corresponding X and Y points
        # Solves issue of multiple places with same name
        for row in readcsv:
            if row['English_Name'] not in ref:
                ref[row['English_Name']] = [[float(row['X']), float(row['Y'])]]
            else:
                ref[row['English_Name']].append([float(row['X']), float(row['Y'])])
    return ref


def create_coordinates_dict(address, ref1, ref2):
    # Building geocoder output dictionary
    # Checks address against townlands reference
    # If no matches, will check against counties reference
    coordinates = {}
    for item in address:
        if item in ref1:
            coordinates.update({item: ref1[item]})
            break
            # If in reference, add to output dictionary and break from loop
            # Will not attempt to find subsequent address fields once it has a match
    if len(coordinates) == 0:
        # If no match was found in townlands reference
        item = address[-1]
        if item in ref2:
            coordinates.update({item: ref2[item]})
    return coordinates


def generate_output(coordinates):
    # Format output dictionary into HTML
    if len(coordinates) == 0:
        # No matches were found in either dictionary
        output = "<p>No match for this address.</p>"
    else:
        # Build HTML table
        output = "<table><tr><th>Location</th><th>X</th><th>Y</th></tr>"
        for k, v in coordinates.items():
            for item in v:
                output += "<tr><td>" + k + "</td><td>" + str(item[0]) + "</td><td>" + str(item[1]) + "</td></tr>"
        output += "</table>"
    return output


townlands = create_reference_dict(townlands_csv)  # Create townlands reference
counties = create_reference_dict(counties_csv)  # Create counties reference


@app.route('/', methods=['GET', 'POST'])
def geocode():
    # Run for site index page, listen for get and post requests
    if request.method != 'POST':
        # Render standard page on get request
        return render_template('index.html')
    address_full = request.form['address'].upper()  # Retrieve address from html form post request
    address_split = address_full.split(', ')
    coordinates = create_coordinates_dict(address_split, townlands, counties)  # Create geocoder output dictionary
    if len(coordinates) >0:
        raw_points = list(coordinates.values())[0]  # Retrieve X and Y components for mapping
    else:
        raw_points = []
    output = generate_output(coordinates)
    return render_template('index.html', output=Markup(output), for_mapping=raw_points)


if __name__ == '__main__':
    app.run(debug=True)

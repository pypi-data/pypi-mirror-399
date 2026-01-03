#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import argparse
import requests
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

__author__ = "Alan Viars"

def is_xml_string(xml_string):
    try:
        ET.fromstring(xml_string)
        return True
    except ET.ParseError as e:
        # print(f"XML parsing error: {e}")
        return False


def check_fhir_metadata(url):
    try:
        r = requests.get(url)
    except requests.RequestException as e:
        return {'error': str(e), 'url': url, 'found': False}
    
    results = {'http_status_code': str(r.status_code),
               'url': url, 'found': False}
    if r.status_code == 200:
        try:
            data = r.json()
            results['data'] = data
            if data.get('resourceType','')=='CapabilityStatement':
                results['found'] = True
        except json.JSONDecodeError as e:
            error_msg = f"JSON decoding error at {url}.  The content may not be valid JSON. {e.msg}"
            results['error'] = error_msg # "Unable to parse decode JSON at %s." % url
            results['data'] = r.text
        if not results['found']:
            if is_xml_string(r.text):
                results['found'] = True
                del results['error']
    else:
        results['error'] = "HTTP status code %s returned from %s." % (r.status_code, url)
    return results


def check_smart_discovery(url):
    try:
        r = requests.get(url)
    except requests.RequestException as e:
        return {'error': str(e), 'url': url, 'found': False}
    
    results = {'http_status_code': str(r.status_code),
               'url': url, 'found': False}
    if r.status_code == 200:
        try:
            data = r.json()
            results['data'] = data
            results['found'] = True
        except json.JSONDecodeError as e:
            error_msg = f"JSON decoding error at {url}.  The content may not be valid JSON. {e.msg}"
            results['error'] = error_msg #"Unable to parse decode JSON at %s." % url
            results['data'] = r.text
    else:
        results['error'] = "HTTP status code %s returned from %s." % (r.status_code, url)
    return results


def check_oidc_discovery(url):
    try:
        r = requests.get(url)
    except requests.RequestException as e:
        return {'error': str(e), 'url': url, 'found': False}
    
    results = {'http_status_code': str(r.status_code),
               'url': url, 'found': False}
    if r.status_code == 200:
        try:
            data = r.json()
            results['data'] = data
            results['found'] = True
            #inspect data for relevant fields

        except json.JSONDecodeError as e:
            error_msg = f"JSON decoding error at {url}.  The content may not be valid JSON. {e.msg}"
            results['error'] = error_msg # "Unable to parse decode JSON at %s." % url
            results['data'] = r.text
    else:
        results['error'] = "HTTP status code %s returned from %s." % (r.status_code, url)
    return results


def check_oauth2_discovery(url):
    try:
        r = requests.get(url)
    except requests.RequestException as e:
        return {'error': str(e), 'url': url, 'found': False}
    
    results = {'http_status_code': str(r.status_code),
               'url': url, 'found': False}
    if r.status_code == 200:
        try:
            data = r.json()
            results['data'] = data
            results['found'] = True
            #inspect data for relevant fields

        except json.JSONDecodeError as e:
            error_msg = f"JSON decoding error at {url}.  The content may not be valid JSON. {e.msg}"
            results['error'] = error_msg # "Unable to parse decode JSON at %s." % url
            results['data'] = r.text
    else:
        results['error'] = "HTTP status code %s returned from %s." % (r.status_code, url)
    return results


def check_for_documentation_ui(urls):
    results = {'found': False}
    for url in urls:
        result ={'url': url, 'found': False}
        try:
            r = requests.get(url)
            result = {'http_status_code': str(r.status_code),
                  'url': url, 'found': False}
            if r.status_code == 200:
                result['found'] = True
                results['found'] = True
        except requests.RequestException as e:
            result = {'error': str(e), 'url': url, 'found': False,
                      'http_status_code': None}
        results[url] = result
    return results


def check_for_swagger_json(urls):
    results = {'found': False}
    for url in urls:
        result ={'url': url, 'found': False}
        try:
            r = requests.get(url)
            if r.status_code == 200:
                try:
                    data = r.json()
                    result['data'] = data
                    result['found'] = True
                    result['http_status_code'] = str(r.status_code)
                    results['found'] = True
                except json.JSONDecodeError:
                    result['error'] = "JSON was not found at %s." % url
                    result['data'] = r.text
                    result['http_status_code'] = None
        except requests.RequestException as e:
            result = {'error': str(e), 'url': url, 'found': False}
       
        results[url] = result
    return results

def check_if_url_is_valid(url):

    try:
        r = requests.get(url)
        return True
    except requests.RequestException as e:
        url = url+"/metadata"
        try:
            r = requests.get(url)
            return True
        except requests.RequestException as e2:
            return False
    return False

def endpoints_to_search(hostname, fhir_prefix=""):
    if hostname.endswith('/'):
        hostname = hostname[:-1]
    if fhir_prefix.endswith('/'):
        fhir_prefix = fhir_prefix[:-1]

    target_endpoints = {"hostname": hostname, "fhir_prefix": fhir_prefix}
    
    wellknown_endpoints = {"wellknown_discover_urls":{'smart_url_1': hostname +'/.well-known/smart-configuration',
                                                      'smart_url_2': hostname + fhir_prefix + '/.well-known/smart-configuration',
                           'oidc_url': hostname +'/.well-known/openid-configuration',
                           'oauth2_url': hostname + '/.well-known/oauth-authorization-server'}}
    

    documentation_endpoints = { 'swagger_json_url': [hostname +'/swagger.json', 
                                                     hostname + '/openapi.json', 
                                                     hostname + '/api/swagger.json',
                                                     hostname + '/api/openapi.json', 
                                                     hostname + '/swagger/v1/swagger.json'],
                                'swagger_docs_url': [hostname + '/swagger', 
                                                     hostname + '/docs', 
                                                     hostname + '/api-docs', 
                                                     hostname + '/documentation']}
    
    fhir_endpoints = {"fhir_endpoints":{'fhir_capability_url':  hostname + fhir_prefix + "/metadata"}}
    endpoints = {}
    endpoints.update(target_endpoints)
    endpoints.update(wellknown_endpoints)
    endpoints.update(documentation_endpoints)
    endpoints.update(fhir_endpoints)
    result = {"endpoints_to_search": endpoints}
    return result


def split_url(url):
    
    parsed_url = urlparse(url)
    hostname = f"{parsed_url.scheme}://{parsed_url.netloc}"
    fhir_prefix = parsed_url.path
    if fhir_prefix.endswith('/'):
        fhir_prefix = fhir_prefix[:-1]
    if fhir_prefix.endswith('/metadata'):
        fhir_prefix = fhir_prefix[:-9]  # remove '/metadata' if present
    return hostname, fhir_prefix


def remove_metadata_from_prefix(fhir_prefix):
    if fhir_prefix.endswith('/metadata'):
        fhir_prefix = fhir_prefix[:-9]  # remove '/metadata' if present
    return fhir_prefix


def build_result_report(result, include_details=False):
    report = {}
    report['details'] = {}
    report['details']['fhir_metadata'] = check_fhir_metadata(result['endpoints_to_search']['fhir_endpoints']['fhir_capability_url'])  
    report['details']['oidc_discovery'] = check_oidc_discovery(result['endpoints_to_search']['wellknown_discover_urls']['oidc_url'])
    report['details']['oauth2_discovery'] = check_oauth2_discovery(result['endpoints_to_search']['wellknown_discover_urls']['oauth2_url'])
    report['details']['smart_discovery_1'] = check_smart_discovery(result['endpoints_to_search']['wellknown_discover_urls']['smart_url_1'])
    report['details']['smart_discovery_2'] = check_smart_discovery(result['endpoints_to_search']['wellknown_discover_urls']['smart_url_2'])
    report['details']['documentation_ui'] = check_for_documentation_ui(result['endpoints_to_search']['swagger_docs_url'])
    report['details']['swagger_json'] = check_for_swagger_json(result['endpoints_to_search']['swagger_json_url'])
    report['report'] = {}
    report['report']['fhir_metadata'] = {'url': report['details']['fhir_metadata']['url'], 'found': report['details']['fhir_metadata']['found']}
    report['report']['oidc_discovery'] = {'url': report['details']['oidc_discovery']['url'], 'found': report['details']['oidc_discovery']['found']}
    report['report']['oauth2_discovery'] = {'url': report['details']['oauth2_discovery']['url'], 'found': report['details']['oauth2_discovery']['found']}
    report['report']['smart_discovery_1'] = {'url': report['details']['smart_discovery_1']['url'], 'found': report['details']['smart_discovery_1']['found']}
    report['report']['smart_discovery_2'] = {'url': report['details']['smart_discovery_2']['url'], 'found': report['details']['smart_discovery_2']['found']}
    report['report']['documentation_ui'] = {'found': report['details']['documentation_ui']['found']}
    for url_result in report['details']['documentation_ui'].values():
        if isinstance(url_result, dict) and 'url' in url_result:
            report['report']['documentation_ui'][url_result['url']] = url_result['found']
    report['report']['swagger_json'] = {'found': report['details']['swagger_json']['found']}
    for url_result in report['details']['swagger_json'].values():
        if isinstance(url_result, dict) and 'url' in url_result:
            report['report']['swagger_json'][url_result['url']] = url_result['found']   
    if not include_details:
        del report['details']
    return report


def fhir_recognizer(url, include_details=True):
    hostname, fhir_prefix = split_url(url)
    fhir_prefix = remove_metadata_from_prefix(fhir_prefix)
    result = endpoints_to_search(hostname, fhir_prefix)
    result = build_result_report(result, include_details=include_details)
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Search for FHIR and related endpoints on a given URL/host.')
    parser.add_argument('--url', '-U', '-u', type=str, help='The full FHIR URL where metadata should be found. (e.g., https://example.com/fhir)')
    parser.add_argument('--hostname', '-H', type=str, help='The target server hostname (e.g., https://example.com).')
    parser.add_argument('--fhir_prefix', '-F', type=str, default='', help='The FHIR API prefix (e.g., /fhir).')
    parser.add_argument('--all', '-A', action='store_true', help='Include the full details of each endpoint check in the output.')
    args = parser.parse_args()

    # Get the hostname and optional FHIR prefix from command line arguments
    if not args.url and not args.hostname:
        print("Error: You must provide either --url or --hostname")
        sys.exit(1)
    
    
    if args.url:
        args.hostname, args.fhir_prefix = split_url(args.url)
    else:
        if not args.hostname:
            print("Error: You must provide --hostname/-H if --url/-U is not provided. Be sure and provide a FHIR prefix with -F option when using -H option.")
            sys.exit(1)
    if args.fhir_prefix:
        # strip the metadata on the end if present.
        args.fhir_prefix = remove_metadata_from_prefix(args.fhir_prefix)
    if not check_if_url_is_valid(args.hostname+args.fhir_prefix):
        print(f"Error: The provided URL {args.hostname}{args.fhir_prefix} is not valid, reachable, or there is a problem with the SSL certificate.")
        sys.exit(1)
    result = endpoints_to_search(args.hostname, args.fhir_prefix)
    result = build_result_report(result, include_details=args.all)
    print(json.dumps(result, indent=2))
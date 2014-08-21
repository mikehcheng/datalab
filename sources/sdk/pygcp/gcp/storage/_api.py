# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Implements Storage HTTP API wrapper."""

import urllib
import gcp._util as _util


class Api(object):
  """A helper class to issue Storage HTTP requests."""

  # TODO(nikhilko): Use named placeholders in these string templates.
  _ENDPOINT = 'https://www.googleapis.com/storage/v1'
  _DOWNLOAD_ENDPOINT = 'https://www.googleapis.com/download/storage/v1'
  _UPLOAD_ENDPOINT = 'https://www.googleapis.com/upload/storage/v1'
  _BUCKET_PATH = '/b/%s'
  _OBJECT_PATH = '/b/%s/o/%s'
  _OBJECT_COPY_PATH = '/b/%s/o/%s/copyTo/b/%s/o/%s'

  _MAX_RESULTS = 100

  def __init__(self, credentials, project_id):
    """Initializes the Storage helper with context information.

    Args:
      credentials: the credentials to use to authorize requests.
      project_id: the project id to associate with requests.
    """
    self._credentials = credentials
    self._project_id = project_id

  @property
  def project_id(self):
    """The project_id associated with this API client."""
    return self._project_id

  def buckets_get(self, bucket, projection='noAcl'):
    """Issues a request to retrieve information about a bucket.

    Args:
      bucket: the name of the bucket.
      projection: the projection of the bucket information to retrieve.
    Returns:
      A parsed bucket information dictionary.
    Raises:
      Exception if there is an error performing the operation.
    """
    url = Api._ENDPOINT + (Api._BUCKET_PATH % bucket)
    return _util.Http.request(url, credentials=self._credentials)

  def buckets_list(self, projection='noAcl', max_results=0, page_token=None):
    """Issues a request to retrieve the list of buckets.

    Args:
      projection: the projection of the bucket information to retrieve.
      max_results: an optional maximum number of objects to retrieve.
      page_token: an optional token to continue the retrieval.
    Returns:
      A parsed list of bucket information dictionaries.
    Raises:
      Exception if there is an error performing the operation.
    """
    if max_results == 0:
      max_results = Api._MAX_RESULTS

    args = {'project': self._project_id, 'maxResults': max_results}
    if projection is not None:
      args['projection'] = projection
    if page_token is not None:
      args['pageToken'] = page_token

    url = Api._ENDPOINT + (Api._BUCKET_PATH % '')
    return _util.Http.request(url, args=args, credentials=self._credentials)

  def object_download(self, bucket, key):
    """Reads the contents of an object as text.

    Args:
      bucket: the name of the bucket containing the object.
      key: the key of the object to be read.
    Returns:
      The text content within the object.
    Raises:
      Exception if the object could not be read from.
    """
    args = {'alt': 'media'}

    url = Api._DOWNLOAD_ENDPOINT + (Api._OBJECT_PATH % (bucket, urllib.quote_plus(key)))
    return _util.Http.request(url, args=args, credentials=self._credentials, raw_response=True)

  def object_upload(self, bucket, key, content, content_type):
    """Writes text content to the object.

    Args:
      bucket: the name of the bucket containing the object.
      key: the key of the object to be read.
      content: the text content to be writtent.
      content_type: the type of text content.
    Raises:
      Exception if the object could not be written to.
    """
    args = {'uploadType': 'media', 'name': key}
    headers = {'Content-Type': content_type}

    url = Api._UPLOAD_ENDPOINT + (Api._OBJECT_PATH % (bucket, ''))
    return _util.Http.request(url, args=args, data=content, headers=headers,
                              credentials=self._credentials, raw_response=True)

  def objects_copy(self, source_bucket, source_key, target_bucket, target_key):
    """Updates the metadata associated with an object.

    Args:
      source_bucket: the name of the bucket containing the source object.
      source_key: the key of the source object being copied.
      target_bucket: the name of the bucket that will contain the copied object.
      target_key: the key of the copied object.
    Returns:
      A parsed object information dictionary.
    Raises:
      Exception if there is an error performing the operation.
    """
    url = Api._ENDPOINT + (Api._OBJECT_COPY_PATH % (source_bucket, urllib.quote_plus(source_key),
                                                    target_bucket, urllib.quote_plus(target_key)))
    return _util.Http.request(url, method='POST', credentials=self._credentials)

  def objects_delete(self, bucket, key):
    """Deletes the specified object.

    Args:
      bucket: the name of the bucket.
      key: the key of the object within the bucket.
    Raises:
      Exception if there is an error performing the operation.
    """
    url = Api._ENDPOINT + (Api._OBJECT_PATH % (bucket, urllib.quote_plus(key)))
    return _util.Http.request(url, method='DELETE', credentials=self._credentials)

  def objects_get(self, bucket, key, projection='noAcl'):
    """Issues a request to retrieve information about an object.

    Args:
      bucket: the name of the bucket.
      key: the key of the object within the bucket.
      projection: the projection of the object to retrieve.
    Returns:
      A parsed object information dictionary.
    Raises:
      Exception if there is an error performing the operation.
    """
    args = {}
    if projection is not None:
      args['projection'] = projection

    url = Api._ENDPOINT + (Api._OBJECT_PATH % (bucket, urllib.quote_plus(key)))
    return _util.Http.request(url, args=args, credentials=self._credentials)

  def objects_list(self, bucket, prefix=None, delimiter=None, projection='noAcl', versions=False,
                   max_results=0, page_token=None):
    """Issues a request to retrieve information about an object.

    Args:
      bucket: the name of the bucket.
      prefix: an optional key prefix.
      delimiter: an optional key delimiter.
      projection: the projection of the objects to retrieve.
      versions: whether to list each version of a file as a distinct object.
      max_results: an optional maximum number of objects to retrieve.
      page_token: an optional token to continue the retrieval.
    Returns:
      A parsed list of object information dictionaries.
    Raises:
      Exception if there is an error performing the operation.
    """
    if max_results == 0:
      max_results = Api._MAX_RESULTS

    args = {'maxResults': max_results}
    if prefix is not None:
      args['prefix'] = prefix
    if delimiter is not None:
      args['delimiter'] = delimiter
    if projection is not None:
      args['projection'] = projection
    if versions:
      args['versions'] = 'true'
    if page_token is not None:
      args['pageToken'] = page_token

    url = Api._ENDPOINT + (Api._OBJECT_PATH % (bucket, ''))
    return _util.Http.request(url, args=args, credentials=self._credentials)

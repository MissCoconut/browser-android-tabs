# Copyright 2018 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import json
import shutil
import tempfile
import unittest

from telemetry.internal.browser import browser_finder
from telemetry.testing import options_for_unittests

from core import perf_benchmark


class PerfBenchmarkTest(unittest.TestCase):
  def setUp(self):
    self._output_dir = tempfile.mkdtemp()

  def tearDown(self):
    shutil.rmtree(self._output_dir, ignore_errors=True)

  def _ExpectAdTaggingProfileFiles(self, browser_options, expect_present):
    files_to_copy = browser_options.profile_files_to_copy

    local_state_to_copy = [
        (s, d) for (s, d) in files_to_copy if d == 'Local State']
    ruleset_data_to_copy = [
        (s, d) for (s, d) in files_to_copy if d.endswith('Ruleset Data')]

    num_expected_matches = 1 if expect_present else 0
    self.assertEqual(num_expected_matches, len(local_state_to_copy))
    self.assertEqual(num_expected_matches, len(ruleset_data_to_copy))


  def testVariationArgs(self):
    benchmark = perf_benchmark.PerfBenchmark()
    options = options_for_unittests.GetCopy()
    options.chrome_root = self._output_dir
    options.browser_type = "any"
    possible_browser = browser_finder.FindBrowser(options)
    if possible_browser is None:
      return
    target_os = perf_benchmark.PerfBenchmark.FixupTargetOS(
        possible_browser.target_os)
    self.assertIsNotNone(target_os)

    testing_config = json.dumps({
      "OtherPlatformStudy": [{
          "platforms": ["fake_platform"],
          "experiments": [{
              "name": "OtherPlatformFeature",
              "enable_features": ["NonExistentFeature"]
          }]
      }],
      "TestStudy": [{
          "platforms": [target_os],
          "experiments": [{
              "name": "TestFeature",
              "params": { "param1" : "value1" },
              "enable_features": ["Feature1", "Feature2"],
              "disable_features": ["Feature3", "Feature4"]}]}]})
    variations_dir = os.path.join(self._output_dir, "testing", "variations")
    os.makedirs(variations_dir)

    fieldtrial_path = os.path.join(
        variations_dir, "fieldtrial_testing_config.json")
    with open(fieldtrial_path, "w") as f:
      f.write(testing_config)

    benchmark.CustomizeBrowserOptions(options.browser_options)

    expected_args = [
      "--enable-features=Feature1<TestStudy,Feature2<TestStudy",
      "--disable-features=Feature3<TestStudy,Feature4<TestStudy",
      "--force-fieldtrials=TestStudy/TestFeature",
      "--force-fieldtrial-params=TestStudy.TestFeature:param1/value1"
    ]
    for arg in expected_args:
      self.assertIn(arg, options.browser_options.extra_browser_args)

    # Test 'reference' type, which has no variation params applied by default.
    benchmark = perf_benchmark.PerfBenchmark()
    options = options_for_unittests.GetCopy()
    options.chrome_root = self._output_dir
    options.browser_options.browser_type = 'reference'
    benchmark.CustomizeBrowserOptions(options.browser_options)

    for arg in expected_args:
      self.assertNotIn(arg, options.browser_options.extra_browser_args)

    # Test compatibility mode, which has no variation params applied by default.
    benchmark = perf_benchmark.PerfBenchmark()
    options = options_for_unittests.GetCopy()
    options.chrome_root = self._output_dir
    options.browser_options.compatibility_mode = ['no-field-trials']
    benchmark.CustomizeBrowserOptions(options.browser_options)

    for arg in expected_args:
      self.assertNotIn(arg, options.browser_options.extra_browser_args)

  def testNoAdTaggingRuleset(self):
    benchmark = perf_benchmark.PerfBenchmark()
    options = options_for_unittests.GetCopy()

    # Set the chrome root to avoid using a ruleset from an existing "Release"
    # out dir.
    options.chrome_root = self._output_dir
    benchmark.CustomizeBrowserOptions(options.browser_options)
    self._ExpectAdTaggingProfileFiles(options.browser_options, False)

  def testAdTaggingRulesetReference(self):
    os.makedirs(os.path.join(
        self._output_dir, 'gen', 'components', 'subresource_filter',
        'tools','GeneratedRulesetData'))

    benchmark = perf_benchmark.PerfBenchmark()
    options = options_for_unittests.GetCopy()
    options.browser_options.browser_type = 'reference'

    # Careful, do not parse the command line flag for 'chromium-output-dir', as
    # that sets the global os environment variable CHROMIUM_OUTPUT_DIR,
    # affecting other tests. See http://crbug.com/843994.
    options.chromium_output_dir = self._output_dir

    benchmark.CustomizeBrowserOptions(options.browser_options)
    self._ExpectAdTaggingProfileFiles(options.browser_options, False)

  def testAdTaggingRuleset(self):
    os.makedirs(os.path.join(
        self._output_dir, 'gen', 'components', 'subresource_filter',
        'tools','GeneratedRulesetData'))

    benchmark = perf_benchmark.PerfBenchmark()
    options = options_for_unittests.GetCopy()

    # Careful, do not parse the command line flag for 'chromium-output-dir', as
    # that sets the global os environment variable CHROMIUM_OUTPUT_DIR,
    # affecting other tests. See http://crbug.com/843994.
    options.chromium_output_dir = self._output_dir

    benchmark.CustomizeBrowserOptions(options.browser_options)
    self._ExpectAdTaggingProfileFiles(options.browser_options, True)

  def testAdTaggingRulesetNoExplicitOutDir(self):
    # Make sure _output_dir points to Chrome's root and not the traditional
    # output directory.
    os.makedirs(os.path.join(
        self._output_dir, 'out','Release','gen', 'components',
        'subresource_filter', 'tools','GeneratedRulesetData'))

    benchmark = perf_benchmark.PerfBenchmark()
    options = options_for_unittests.GetCopy()
    options.chrome_root = self._output_dir
    options.browser_options.browser_type = "release"

    benchmark.CustomizeBrowserOptions(options.browser_options)
    self._ExpectAdTaggingProfileFiles(options.browser_options, True)

  def testAdTaggingRulesetNoExplicitOutDirAndroidChromium(self):
    # Make sure _output_dir points to Chrome's root and not the traditional
    # output directory.
    os.makedirs(os.path.join(
        self._output_dir, 'out','Default','gen', 'components',
        'subresource_filter', 'tools','GeneratedRulesetData'))

    benchmark = perf_benchmark.PerfBenchmark()
    options = options_for_unittests.GetCopy()
    options.chrome_root = self._output_dir

    # android-chromium is special cased to search for anything.
    options.browser_options.browser_type = "android-chromium"

    benchmark.CustomizeBrowserOptions(options.browser_options)
    self._ExpectAdTaggingProfileFiles(options.browser_options, True)

  def testAdTaggingRulesetOutputDirNotFound(self):
    # Same as the above test but use Debug instead of Release. This should
    # cause the benchmark to fail to find the ruleset because we only check
    # directories matching the browser_type.
    os.makedirs(os.path.join(
        self._output_dir, 'out','Debug','gen', 'components',
        'subresource_filter', 'tools','GeneratedRulesetData'))

    benchmark = perf_benchmark.PerfBenchmark()
    options = options_for_unittests.GetCopy()
    options.chrome_root = self._output_dir
    options.browser_options.browser_type = "release"

    benchmark.CustomizeBrowserOptions(options.browser_options)
    self._ExpectAdTaggingProfileFiles(options.browser_options, False)

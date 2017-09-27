"""Tests for psychopy.data.DataHandler"""
from __future__ import print_function

from builtins import str
from builtins import range
from builtins import object
import os, glob
from os.path import join as pjoin
import shutil
from tempfile import mkdtemp, mkstemp
import numpy as np
import pytest

from psychopy import data
from psychopy.tools.filetools import fromFile
from psychopy.tests import utils
from psychopy.constants import PY3

thisPath = os.path.split(__file__)[0]
fixturesPath = os.path.join(thisPath,'..','data')


class TestTrialHandler(object):
    def setup_class(self):
        self.temp_dir = mkdtemp(prefix='psychopy-tests-testdata')
        self.rootName = 'test_data_file'
        self.random_seed = 100

    def teardown_class(self):
        shutil.rmtree(self.temp_dir)

    def test_underscores_in_datatype_names(self):
        trials = data.TrialHandler([], 1, autoLog=False)
        trials.data.addDataType('with_underscore')
        for trial in trials:  # need to run trials or file won't be saved
            trials.addData('with_underscore', 0)
        base_data_filename = pjoin(self.temp_dir, self.rootName)
        trials.saveAsExcel(base_data_filename)
        trials.saveAsText(base_data_filename, delim=',')

        # Make sure the file is there
        data_filename = base_data_filename + '.csv'
        assert os.path.exists(data_filename), "File not found: %s" %os.path.abspath(data_filename)

        # Make sure the header line is correct
        # We open the file with universal newline support (PEP-278).
        if PY3:
            with open(data_filename, 'r', newline=None) as f:
                header = f.readline()
        else:
            with open(data_filename, 'rU') as f:
                header = f.readline()

        expected_header = u'n,with_underscore_mean,with_underscore_raw,with_underscore_std,order\n'
        if expected_header != header:
            print(base_data_filename)
            print(repr(expected_header),type(expected_header),len(expected_header))
            print(repr(header), type(header), len(header))
        assert expected_header == str(header)

    def test_psydat_filename_collision_renaming(self):
        for count in range(1,20):
            trials = data.TrialHandler([], 1, autoLog=False)
            trials.data.addDataType('trialType')
            for trial in trials:#need to run trials or file won't be saved
                trials.addData('trialType', 0)
            base_data_filename = pjoin(self.temp_dir, self.rootName)

            trials.saveAsPickle(base_data_filename)

            # Make sure the file just saved is there
            data_filename = base_data_filename + '.psydat'
            assert os.path.exists(data_filename), "File not found: %s" %os.path.abspath(data_filename)

            # Make sure the correct number of files for the loop are there. (No overwriting by default).
            matches = len(glob.glob(os.path.join(self.temp_dir, self.rootName + "*.psydat")))
            assert matches==count, "Found %d matching files, should be %d" % (matches, count)
    def test_psydat_filename_collision_overwriting(self):
        for count in [1, 10, 20]:
            trials = data.TrialHandler([], 1, autoLog=False)
            trials.data.addDataType('trialType')
            for trial in trials:#need to run trials or file won't be saved
                trials.addData('trialType', 0)
            base_data_filename = pjoin(self.temp_dir, self.rootName+'overwrite')

            trials.saveAsPickle(base_data_filename, fileCollisionMethod='overwrite')

            # Make sure the file just saved is there
            data_filename = base_data_filename + '.psydat'
            assert os.path.exists(data_filename), "File not found: %s" %os.path.abspath(data_filename)

            # Make sure the correct number of files for the loop are there. (No overwriting by default).
            matches = len(glob.glob(os.path.join(self.temp_dir, self.rootName + "*overwrite.psydat")))
            assert matches==1, "Found %d matching files, should be %d" % (matches, count)

    def test_multiKeyResponses(self):
        pytest.skip()  # temporarily; this test passed locally but not under travis, maybe PsychoPy version of the .psyexp??

        dat = fromFile(os.path.join(fixturesPath,'multiKeypressTrialhandler.psydat'))
        #test csv output
        dat.saveAsText(pjoin(self.temp_dir, 'testMultiKeyTrials.csv'), appendFile=False)
        utils.compareTextFiles(pjoin(self.temp_dir, 'testMultiKeyTrials.csv'), pjoin(fixturesPath,'corrMultiKeyTrials.csv'))
        #test xlsx output
        dat.saveAsExcel(pjoin(self.temp_dir, 'testMultiKeyTrials.xlsx'), appendFile=False)
        utils.compareXlsxFiles(pjoin(self.temp_dir, 'testMultiKeyTrials.xlsx'), pjoin(fixturesPath,'corrMultiKeyTrials.xlsx'))

    def test_psydat_filename_collision_failure(self):
        with pytest.raises(IOError):
            for count in range(1,3):
                trials = data.TrialHandler([], 1, autoLog=False)
                trials.data.addDataType('trialType')
                for trial in trials:#need to run trials or file won't be saved
                    trials.addData('trialType', 0)
                base_data_filename = pjoin(self.temp_dir, self.rootName)

                trials.saveAsPickle(base_data_filename, fileCollisionMethod='fail')

    def test_psydat_filename_collision_output(self):
        #create conditions
        conditions=[]
        for trialType in range(5):
            conditions.append({'trialType':trialType})
            #create trials
        trials= data.TrialHandler(trialList=conditions, seed=self.random_seed,
                                  nReps=3, method='fullRandom', autoLog=False)
        # simulate trials
        rng = np.random.RandomState(seed=self.random_seed)

        for thisTrial in trials:
            resp = 'resp' + str(thisTrial['trialType'])
            randResp = rng.rand()
            trials.addData('resp', resp)
            trials.addData('rand',randResp)

        # test summarised data outputs
        trials.saveAsText(pjoin(self.temp_dir, 'testFullRandom.tsv'), stimOut=['trialType'],appendFile=False)#this omits values
        utils.compareTextFiles(pjoin(self.temp_dir, 'testFullRandom.tsv'), pjoin(fixturesPath,'corrFullRandom.tsv'))
        # test wide data outputs
        trials.saveAsWideText(pjoin(self.temp_dir, 'testFullRandom.csv'), delim=',', appendFile=False)#this omits values
        utils.compareTextFiles(pjoin(self.temp_dir, 'testFullRandom.csv'), pjoin(fixturesPath,'corrFullRandom.csv'))

    def test_random_data_output(self):
        # create conditions
        conditions=[]
        for trialType in range(5):
            conditions.append({'trialType':trialType})

        trials = data.TrialHandler(trialList=conditions, seed=self.random_seed,
                                   nReps=3, method='random', autoLog=False)
        # simulate trials
        rng = np.random.RandomState(seed=self.random_seed)

        for thisTrial in trials:
            resp = 'resp' + str(thisTrial['trialType'])
            randResp = rng.rand()
            trials.addData('resp', resp)
            trials.addData('rand', randResp)

        # test summarised data outputs
        trials.saveAsText(pjoin(self.temp_dir, 'testRandom.tsv'), stimOut=['trialType'],appendFile=False)#this omits values
        utils.compareTextFiles(pjoin(self.temp_dir, 'testRandom.tsv'), pjoin(fixturesPath,'corrRandom.tsv'))
        # test wide data outputs
        trials.saveAsWideText(pjoin(self.temp_dir, 'testRandom.csv'), delim=',', appendFile=False)#this omits values
        utils.compareTextFiles(pjoin(self.temp_dir, 'testRandom.csv'), pjoin(fixturesPath,'corrRandom.csv'))

    def test_comparison_equals(self):
        t1 = data.TrialHandler([dict(foo=1)], 2)
        t2 = data.TrialHandler([dict(foo=1)], 2)
        assert t1 == t2

    def test_comparison_equals_after_iteration(self):
        t1 = data.TrialHandler([dict(foo=1)], 2)
        t2 = data.TrialHandler([dict(foo=1)], 2)
        t1.__next__()
        t2.__next__()
        assert t1 == t2

    def test_comparison_not_equal(self):
        t1 = data.TrialHandler([dict(foo=1)], 2)
        t2 = data.TrialHandler([dict(foo=1)], 3)
        assert t1 != t2

    def test_comparison_not_equal_after_iteration(self):
        t1 = data.TrialHandler([dict(foo=1)], 2)
        t2 = data.TrialHandler([dict(foo=1)], 3)
        t1.__next__()
        t2.__next__()
        assert t1 != t2


class TestTrialHandlerOutput(object):
    def setup_class(self):
        self.temp_dir = mkdtemp(prefix='psychopy-tests-testdata')
        self.random_seed = 100

    def teardown_class(self):
        shutil.rmtree(self.temp_dir)

    def setup_method(self, method):
        # create conditions
        conditions = []
        for trialType in range(5):
            conditions.append({'trialType':trialType})

        self.trials = data.TrialHandler(trialList=conditions,
                                        seed=self.random_seed,
                                        nReps=3, method='random', autoLog=False)
        # simulate trials
        rng = np.random.RandomState(seed=self.random_seed)

        for thisTrial in self.trials:
            resp = 'resp' + str(thisTrial['trialType'])
            randResp = rng.rand()
            self.trials.addData('resp', resp)
            self.trials.addData('rand', randResp)

    def test_output_no_filename_no_delim(self):
        _, path = mkstemp(dir=self.temp_dir)
        delim = None
        self.trials.saveAsWideText(path, delim=delim)

        expected_suffix = '.tsv'
        assert os.path.isfile(path + expected_suffix)

        expected_delim = '\t'
        expected_header = ['TrialNumber']
        expected_header.extend(list(self.trials.trialList[0].keys()))
        expected_header.extend(self.trials.data.dataTypes)
        expected_header = expected_delim.join(expected_header) + '\n'

        # Universal newline support.
        if PY3:
            with open(path + expected_suffix, 'r', newline=None) as f:
                header = f.readline()
        else:
            with open(path + expected_suffix, 'rU') as f:
                header = f.readline()

        assert header == expected_header

    def test_output_no_filename_comma_delim(self):
        _, path = mkstemp(dir=self.temp_dir)
        delim = ','
        self.trials.saveAsWideText(path, delim=delim)

        expected_suffix = '.csv'
        assert os.path.isfile(path + expected_suffix)

        expected_header = ['TrialNumber']
        expected_header.extend(list(self.trials.trialList[0].keys()))
        expected_header.extend(self.trials.data.dataTypes)
        expected_header = delim.join(expected_header) + '\n'

        # Universal newline support.
        if PY3:
            with open(path + expected_suffix, 'r', newline=None) as f:
                header = f.readline()
        else:
            with open(path + expected_suffix, 'rU') as f:
                header = f.readline()

        assert header == expected_header

    def test_output_no_filename_tab_delim(self):
        _, path = mkstemp(dir=self.temp_dir)
        delim = '\t'
        self.trials.saveAsWideText(path, delim=delim)

        expected_suffix = '.tsv'
        assert os.path.isfile(path + expected_suffix)

        expected_header = ['TrialNumber']
        expected_header.extend(list(self.trials.trialList[0].keys()))
        expected_header.extend(self.trials.data.dataTypes)
        expected_header = delim.join(expected_header) + '\n'

        # Universal newline support.
        if PY3:
            with open(path + expected_suffix, 'r', newline=None) as f:
                header = f.readline()
        else:
            with open(path + expected_suffix, 'rU') as f:
                header = f.readline()

        assert header == expected_header

    def test_output_no_filename_semicolon_delim(self):
        _, path = mkstemp(dir=self.temp_dir)
        delim = ';'
        self.trials.saveAsWideText(path, delim=delim)

        expected_suffix = '.txt'
        assert os.path.isfile(path + expected_suffix)

        expected_header = ['TrialNumber']
        expected_header.extend(list(self.trials.trialList[0].keys()))
        expected_header.extend(self.trials.data.dataTypes)
        expected_header = delim.join(expected_header) + '\n'

        # Universal newline support.
        if PY3:
            with open(path + expected_suffix, 'r', newline=None) as f:
                header = f.readline()
        else:
            with open(path + expected_suffix, 'rU') as f:
                header = f.readline()

        assert header == expected_header

    def test_output_csv_suffix_no_delim(self):
        _, path = mkstemp(dir=self.temp_dir, suffix='.csv')
        delim = None
        self.trials.saveAsWideText(path, delim=delim)

        expected_delim = ','
        expected_header = ['TrialNumber']
        expected_header.extend(list(self.trials.trialList[0].keys()))
        expected_header.extend(self.trials.data.dataTypes)
        expected_header = expected_delim.join(expected_header) + '\n'

        # Universal newline support.
        if PY3:
            with open(path, 'r', newline=None) as f:
                header = f.readline()
        else:
            with open(path, 'rU') as f:
                header = f.readline()

        assert header == expected_header

    def test_output_arbitrary_suffix_no_delim(self):
        _, path = mkstemp(dir=self.temp_dir, suffix='.xyz')
        delim = None
        self.trials.saveAsWideText(path, delim=delim)

        expected_suffix = '.tsv'
        assert os.path.isfile(path + expected_suffix)

        expected_delim = '\t'
        expected_header = ['TrialNumber']
        expected_header.extend(list(self.trials.trialList[0].keys()))
        expected_header.extend(self.trials.data.dataTypes)
        expected_header = expected_delim.join(expected_header) + '\n'

        # Universal newline support.
        if PY3:
            with open(path + expected_suffix, 'r', newline=None) as f:
                header = f.readline()
        else:
            with open(path + expected_suffix, 'rU') as f:
                header = f.readline()

        assert header == expected_header

    def test_output_csv_and_semicolon(self):
        _, path = mkstemp(dir=self.temp_dir, suffix='.csv')
        delim = ';'
        self.trials.saveAsWideText(path, delim=delim)

        assert os.path.isfile(path)

        expected_delim = ';'
        expected_header = ['TrialNumber']
        expected_header.extend(list(self.trials.trialList[0].keys()))
        expected_header.extend(self.trials.data.dataTypes)
        expected_header = expected_delim.join(expected_header) + '\n'

        # Universal newline support.
        if PY3:
            with open(path, 'r', newline=None) as f:
                header = f.readline()
        else:
            with open(path, 'rU') as f:
                header = f.readline()

        assert header == expected_header


class TestMultiStairs(object):
    def setup_class(self):
        self.temp_dir = mkdtemp(prefix='psychopy-tests-testdata')
        self.random_seed = 100

    def teardown_class(self):
        shutil.rmtree(self.temp_dir)

    def test_simple(self):
        conditions = data.importConditions(
            pjoin(fixturesPath, 'multiStairConds.xlsx'))
        stairs = data.MultiStairHandler(stairType='simple', conditions=conditions,
                method='random', nTrials=20, name='simpleStairs', autoLog=False)
        exp = data.ExperimentHandler(name='testExp',
                    savePickle=True,
                    saveWideText=True,
                    dataFileName=pjoin(self.temp_dir, 'multiStairExperiment'), autoLog=False)
        rng = np.random.RandomState(seed=self.random_seed)

        exp.addLoop(stairs)

        for intensity,condition in stairs:
            # make data that will cause different stairs to finish different times
            if rng.rand() > condition['startVal']:
                corr=1
            else:corr=0
            stairs.addData(corr)
        stairs.saveAsExcel(pjoin(self.temp_dir, 'multiStairOut'))
        stairs.saveAsPickle(pjoin(self.temp_dir, 'multiStairOut'))#contains more info

    def test_quest(self):
        conditions = data.importConditions(
            pjoin(fixturesPath, 'multiStairConds.xlsx'))
        stairs = data.MultiStairHandler(stairType='quest', conditions=conditions,
                    method='random', nTrials=20, name='QuestStairs', autoLog=False)
        exp = data.ExperimentHandler(name='testExp',
                    savePickle=True,
                    saveWideText=True,
                    dataFileName=pjoin(self.temp_dir, 'multiQuestExperiment'), autoLog=False)
        rng = np.random.RandomState(seed=self.random_seed)

        exp.addLoop(stairs)
        for intensity,condition in stairs:
            # make data that will cause different stairs to finish different times
            if rng.rand() > condition['startVal']:
                corr=1
            else:corr=0
            stairs.addData(corr)
        stairs.saveAsExcel(pjoin(self.temp_dir, 'multiQuestOut'))
        stairs.saveAsPickle(pjoin(self.temp_dir, 'multiQuestOut'))# contains more info


if __name__ == '__main__':
    pytest.main()

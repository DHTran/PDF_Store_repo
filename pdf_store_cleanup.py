import glob
import os
import pandas as pd
import re
import shutil
import filecmp
from Bio import Entrez
from pathlib import Path
from dotenv import load_dotenv
from pdf_store_cleanup import Copy_files
load_dotenv()
Entrez.api_key = os.getenv('Entrez.api_key')
Entrez.email = os.getenv('Entrez.email')

PDF_STORE = Path("/Users/dht/Google Drive File Stream/Shared drives/PDF Store/")
PDF_COPY = Path("/Users/dht/Google Drive File Stream/My Drive/files/PDF_Store_copy/")
PDF_COPY_MOVED = Path(PDF_COPY/'moved_files/')
SUPP_DEST = Path(PDF_COPY/'supp_files')
DATAFILES = Path("/Users/dht/datafiles/pdf_store_repo_files/")
TEST_FOLDER = Path(DATAFILES/"test_folder/")

DIGITS_MATCH = re.compile('^(\d+)')
PARENTHESES_MATCH = re.compile('^.* \(\d+\).pdf')
UP_TO_PARENTHESES_DIGIT = re.compile('(.+?)\(\d+\)')
UP_TO_WHITESPACE = re.compile('^\S+')
PMID_AUTHOR_YEAR= re.compile('^[0-9]+[ ][a-zA-Z-]+[ ][0-9]+$')
PRECEEDING_WHITESPACE = re.compile('^\s+')
PMID_AUTHOR_YEAR_UNDERSCORE = re.compile('^[0-9]+_[a-zA-Z- ]+_[0-9]+.pdf$')

# workflow
# copy_files = Copy_files()
# copy_files.copy_pdfs()
# copy_files.copy_non_google_files()
# copy_files.copy_suppfiles()
# files_not_copies = copy_files.files_not_copied()
# not_copied_df = pd.DataFrame(files_not_copied)
# not_copied_df.to_csv('not_copied.csv', encoding='utf-8')

# files_list = Directory_list(PDF_COPY)
# cleanup = Analyze_pdf_store(files_list.files_list, PDF_COPY)
# pmids = cleanup.find_pmids()
# filenames_matches = cleanup.create_filenames_digit_matches()
# filter_results = cleanup.filter_files(filenames_matches) to see state of files and
# categories to be changed or not
# pmid_pubmed_data, errors = cleanup.get_pubmed_data(pmids) may take >20 min
# pmid_pubmed_data = pd.read_csv(DATAFILES/'pmid_pubmed.csv') to load previous data
# results = cleanup.rename_pmid_files(pmids, pmid_pubmed_data, delete=False)
# change to delete=True to remove files, results list files altered or not
# cleanup.remove_preceeding_spaces(filter_results['preceeding_spaces'], delete=False)
# cleanup.move_supplementals(filter_results['supplementals'], SUPP_DEST, remove=False)
# cleanup.rename_capitalized_extensions(check_file=True, rename=False)


class Copy_files:
    """class to hold methods for filtering and copying files

    Arg:
        source_path = path to source directory (as pathlib Path)
        dest_path = path to destination directory (as pathlib Path)
    """
    # non-pep8
    PDF_STORE = Path("/Users/dht/Google Drive File Stream/Shared drives/PDF Store")
    PDF_COPY = Path("/Users/dht/Google Drive File Stream/My Drive/files/PDF_Store_copy")

    def __init__(self, source_path, dest_path):
        if source_path is None:
            source_path = PDF_STORE
        else:
            self.source_path = source_path
        if dest_path is None:
            dest_path = PDF_COPY
        else:
            self.dest_path = dest_path

    def __repr__(self):
        repr_string = (f"""
        source dir =  {self.source_path},
        dest dir = {self.dest_path}
        """)
        return repr_string

    def copy_pdfs():
        """copy pdf files from the PDF store folder
        to new folder (PDF_Store_copy)
        """
        counter = 0
        for pdf in self.source_path .glob("*.pdf"):
            source_file = pdf
            dest_file = Path(self.dest_path/source_file.name)
            if dest_file.is_file():
                pass
            else:
                print(f"copying {source_file} to {dest_file}")
                # paths to source and destination
                copy_file(source_file, dest_file)
                counter+=1
        print(f"number of files copied = {counter}")

    def copy_non_google_files():
        """copy non .gdoc/.gsheet files to dest_path.
        e.g. Supp .xls or .doc files. uses DIGIT_MATCH (regex for
        names the lead with digits) to select files for copying.
        e.g. 3515341 Supp.xls

        Assumes that pdf files had been copies already. Will also
        skip files that already exist in the destination folder
        """
        file_filter = ['.gdoc', '.gsheet']
        for file_ in self.source_path.glob("*"):
            if file_.suffix in file_filter:
                pass
            else:
                if file_.suffix != ".pdf":
                    if re.match(DIGITS_MATCH, file_.name) and file_.is_file():
                        source_file = file_
                        dest_file = Path(self.dest_path/source_file.name)
                        if dest_file.is_file():
                            pass
                        else:
                            print(f"copying {source_file} to {dest_file}")
                            copy_file(source_file, dest_file)

    def copy_file(source_file, dest_file):
        """uses shutil.copyfile to
        copy source_file to dest_file
        """
        print(f"copying {source_file} to {dest_file}")
        shutil.copyfile(source_file, dest_file)

    def copy_suppfiles():
        """copy all files (and not folders) with 'supp'
        (case-insensitive) to dest path with the
        same name

        Note this is for non-PDF supp files assuming
        copy_pdfs() has been run
        """
        counter = 0
        file_filter = ['.gdoc', '.gsheet']
        for file_ in self.source_path.glob("*"):
            if file_.suffix in file_filter:
                pass
            else:
                filename = file_.name.lower()
                if "supp" in filename and file_.is_file():
                    counter += 1
                    # print(filename)
                    source_file = file_
                    dest_file = Path(self.dest_path/source_file.name)
                    if dest_file.is_file():
                        pass
                    else:
                        print(f"copying {source_file} to {dest_file}")
                        copy_file(source_file, dest_file)
                elif file_.is_dir():
                    print(f"{file_} is a directory")
        print(counter)

    def files_not_copied():
        files_list = []
        counter = 0
        for file_ in self.source_path.glob("*"):
            new_file = Path(self.dest_path/file_.name)
            if not new_file.is_file() and not file_.is_dir():
                counter += 1
                print(file_.name)
                files_list.append(file_.name)
        print(counter)
        return files_list


class Directory_list:
    def __init__(self, directory_path):
        self.directory_path = directory_path
        paths = directory_path.glob("*")
        self.files_list = [f for f in paths if f.is_file()]

    def __repr__(self):
        repr_string = (f"""
        path to analyze {self.directory_path},
        number of files: {len(list(self.files_list))}
        """)
        return repr_string

class Analyze_pdf_store:
    """class to sort/filter PDF directory. Goal is to convert PDF files
    to pmid author year.pdf filename (assuming it's journal article
    with a pubmed pmid)

    PDF files may have one or more duplicate files.  There are also
    non-pmid PDFs, supplementary tables/docs, non-PDF files, and other files

    Args:
        files_list = list of pathlib Paths for each file (is_file() = True)
        directory_path = pathlib Path for PDF directory
    """

    def __init__(self, files_list=None, directory_path=None):
        self.files_list = files_list
        self.directory_path = directory_path

    def __repr__(self):
        repr_string = (f"""
        first five files: {self.files_list[0:4]}
        number of files: {len(list(self.files_list))}

        directory_path: {self.directory_path}
        """)
        return repr_string

    def find_pmids(self, file_list=None):
        """
        Function to sort through list of file paths (using pathlib.glob)
        for duplicates.  Creates dict with putative PMID as key and all
        files that are returned searching for that PMID (excludes any with supp in
        name)

        1) creates list of file names from list of file paths in directory
        2) takes each pmid and looks for all filenames that contain that pmid
            (excludes filenames containing "supp", case insensitive)
        3) creates dict with keys=pmid, and values=list of all filenames with that pmid
        4) check if files with the same pmid are duplicates by checking file sizes
            flag those pmids/files that do not
        5) return list of pmid

        Arg: file_list is list of filenames (not paths)

        """
        pmids = []
        supp_data_filters = ['supp', 'table']
        if file_list is None:
            for file_ in self.files_list:
                pmid = None
                not_supp = any(file_.stem.lower() not in filter_
                               for filter_ in supp_data_filters)
                if not_supp:
                    pmid_match = re.match(DIGITS_MATCH, file_.stem)
                    if pmid_match:
                        pmid = pmid_match.group(0)
                    if pmid and pmid not in pmids:
                        pmids.append(pmid)
        else:
            #assumes is list of file names and not paths
            for file in file_list:
                pmid = None
                name = file.split(".")[0]
                not_supp = any(name.lower() not in filter_
                               for filter_ in supp_data_filters)
                if not_supp:
                    pmid_match = re.match(DIGITS_MATCH, name)
                    if pmid_match:
                        pmid = pmid_match.group(0)
                    if pmid and (pmid not in pmids):
                        pmids.append(pmid)
        return sorted(pmids)

    def match_digits(self, name):
        """matches first string of digits in string and returns,
        returns None if no match
        """
        first_digits_match = re.match(DIGITS_MATCH, name)
        if first_digits_match:
            first_digits = first_digits_match.group(0)
            return first_digits
        else:
            return None

    def create_filenames_digit_matches(self):
        """create a list of tuples from the list of file
        paths in self.files_list where:


        first item = regex extract of preceeding digits in name
        second item = Path.stem
        (if one exists, i.e. pmid number)

        (filename stems, DIGITS_MATCH regex extract)

        The list of tuples is used to facilitate filtering
        of files
        """
        regex_matches = []
        filenames = [filename.name for filename in self.files_list]
        for name in filenames:
            regex_match = self.match_digits(name)
            regex_matches.append(regex_match)
        names_matches_tuple = list(zip(regex_matches, filenames))
        return names_matches_tuple

    def filter_files(self, filenames_matches):
        """
        Takes tuples of (digit_match, filename) where
        digits_match = first string of digits if one exists
        filename = filename.ext

        Sorts into different lists bases on criteria:

        supplementals = 'supp' and 'table' in name or 'ppt',
        'png', 'docx' in name

        digits_match is None followed by:
        - preceeding_spaces = filename has one or more spaces
        at the start
        - no_pmids = no preceeding digits in name
        - pmid_in_name = 'pmid' in filename

        correct_name = pmid author year
        others = remaining files

        Returns a dict with keys corresponding to above
        categories
        """
        index = 0
        supp_data_filters = ['supp', 'table']
        suffix_filters = ['ppt', 'png', 'docx']
        filter_results = {}
        supplementals = []
        pmid_pdf = []
        pmid_in_name = []
        no_pmids = []
        others = []
        correct_name = []
        preceeding_spaces = []
        for digits_match, filename in filenames_matches:
            index += 1
            # skip the Mac Icon directory file
            if filename == 'Icon\r':
                continue
            try:
                filename_stem = filename.split(".")[0]
                filename_suffix = filename.split(".")[1]
            except IndexError:
                print(filename)
            supp_filter_flag = any(supp_filter in filename.lower()
                                   for supp_filter in supp_data_filters)
            suffix_filter_flag = any(suffix_filter in filename.lower()
                                    for suffix_filter in suffix_filters)
            # finds supplemental data files or file extensions in suffix_filters
            if supp_filter_flag or suffix_filter_flag:
                supplementals.append(filename)
            # finds files with no preceeding digits, preceeding spaces
            elif digits_match is None:
                if re.match(PRECEEDING_WHITESPACE, filename):
                    preceeding_spaces.append(filename)
                elif 'pmid' in filename.lower():
                    pmid_in_name.append(filename)
                else:
                    no_pmids.append(filename)
            elif filename == (digits_match + ".pdf"):
                pmid_pdf.append(filename)
            elif re.match(PMID_AUTHOR_YEAR, filename_stem):
                correct_name.append(filename)
            else:
                others.append(filename)
        filter_results['supplementals'] = supplementals
        filter_results['no_pmids'] = no_pmids
        filter_results['pmid_pdf'] = pmid_pdf
        filter_results['preceeding_spaces'] = preceeding_spaces
        filter_results['others'] = others
        filter_results['pmid_in_name'] = pmid_in_name
        filter_results['correct_name'] = correct_name
        return filter_results

    def get_pubmed_data(self, pmids):
        """query Pubmed with Biopython's Entrez module
        extract first author (from AuthorList with regex match
        of first characters up to whitespace; ideally will get
        non-English characters), date, and journal names.

        Save to dict
        """
        pmid_pubmed_data = {}
        errors = []
        for pmid in pmids:
            single_pmid_data = {}
            try:
                record = Entrez.read(Entrez.esummary(db="pubmed", id=pmid))
            except RuntimeError:
                errors.append(pmid)
                continue
            author_list = record[0].get('AuthorList')
            if author_list:
                first_characters = re.match(UP_TO_WHITESPACE, author_list[0])
                if first_characters:
                    first_author = first_characters[0]
            date = record[0].get('PubDate')
            journal = record[0].get('FullJournalName')
            new_filename = pmid+" "+first_author+" "+date[0:4]
            single_pmid_data['first_author'] = first_author
            single_pmid_data['date'] = date
            single_pmid_data['journal'] = journal
            single_pmid_data['new_filename'] = new_filename
            pmid_pubmed_data[pmid] = single_pmid_data
        return pmid_pubmed_data, errors

    def rename_pmid_files(self, pmids, pubmed_data, delete=False, pmid_space_pdf=False):
        """take pmid.pdf and renames to pmid author year.pdf if not a
        duplicate

        Args:
        pmids = list of pmids
        pubmed_data = pandas dataframe with pmid, date, journal, new_filename

        """
        def get_size(file):
            file = Path(file)
            return file.stat().st_size

        results = {}
        correct_files = []
        leading_zeros = []
        not_found_pubmed = []
        renamed = []
        for pmid in pmids:
            correct_filename, correct_file, pmid_pdf = None, None, None
            # avoid converting 00524 to 524 for example
            if pmid[0] != '0':
                pmid_int = int(pmid)
            else:
                print(f"leading 0 for {pmid}")
                leading_zeros.append(pmid)
                continue
            try:
                author_date_year = (
                    pubmed_data.loc[pubmed_data['pmid'] == pmid_int, 'new_filename'].values[0]
                    )
            except Exception as e:
                print(f"error looking up pmid in dataframe {pmid}")
                not_found_pubmed.append(pmid)
                continue
            if pmid_space_pdf:
                pmid_pdf = pmid + " .pdf"
            else:
                pmid_pdf = pmid + ".pdf"
            pmid_pdf_path = Path(self.directory_path/pmid_pdf)
            correct_filename = author_date_year+".pdf"
            correct_file_path = Path(self.directory_path/correct_filename)
            correct_file_exists = correct_file_path.is_file()
            pmid_pdf_exists = pmid_pdf_path.is_file()
            if correct_file_exists:
                correct_file_size = get_size(correct_file_path)
                print(f"correct file {correct_file_path.name} exists")
                correct_files_tuple = (correct_filename, correct_file_size)
                correct_files.append(correct_files_tuple)
                if delete:
                    print(f"deleting {pmid_pdf_path}")
                    pmid_pdf_path.unlink()
            elif pmid_pdf_exists and not correct_file_exists:
                print(f"rename {pmid_pdf_path} to {correct_file_path}")
                pmid_pdf_path.rename(correct_file_path)
                renamed_tuple = (pmid_pdf, correct_filename)
                renamed.append(renamed_tuple)
        results['correct_files'] = correct_files
        results['renamed'] = renamed
        results['not_found_pubmed'] = not_found_pubmed
        results['leading_zeros'] = leading_zeros
        return results

    def rename_capitalized_extensions(self, check_file=True, rename=False):
        """rename capitalized PDF to pdf
        """
        paths = self.directory_path.glob("*")
        files_list = [f for f in paths if f.is_file()]
        for index,file in enumerate(files_list):
            if file.suffix == '.PDF':
                if check_file:
                    print(file)
                    new_file = f"{file.parent}{file.stem}'.pdf'"
                    print(new_file)
                elif rename:
                    new_file = f"{file.parent}{file.stem}'.pdf'"
                    new_path = Path(new_file)
                    print(f"{file} renaming to .pdf ")
                    file.rename(file.with_suffix('.pdf'))
                    file_exists = file.is_file()
                    print(f"old file {file} exists = {file_exists}")
                    new_file_exists = new_path.is_file()
                    print(f"new file {new_file} exists {new_file_exists}")

    def move_supplementals(self, supp_list, dest_path, copy=False, remove=False):
        """moves supplemental files (files with 'supp', 'table' in name or
        'ppt', 'png', or 'docx') to supp_folder. Goal is to remove files
        and facilitate further sorting

        Args: list of supplemental file names (see filter_files method)

        """
        source = self.directory_path
        for file in supp_list:
            source = Path(self.directory_path/file)
            destination = Path(dest_path/file)
            if copy:
                print(f"copying {source} to {destination}")
                Analyze_pdf_store.copy_file(source, destination)
            if remove:
                if source.is_file():
                    print(f"removing {source}")
                    print(f"{source} exists: {source.is_file()}")
                    source.unlink()
                    print(f"{source} exists: {source.is_file()}")
                    print("\n")

    def remove_preceeding_spaces(self, files, delete=False):
        """takes files with preceeding spaces before pmid (e.g. __13431.pdf)
        1) check if removing preceeding spaces and subsequent file already
        exists
        2) if not then renames file
        3) if yes then deletes file

        Args: files = list of files (not paths)
        """
        for file in files:
            old_file = Path(self.directory_path/file)
            file_stem = file.split(".")[0]
            no_whitespace = file_stem.strip()
            correct_name = no_whitespace+".pdf"
            correct_path = Path(self.directory_path/correct_name)
            if delete:
                if correct_path.is_file():
                    # check for existing file of same name
                    continue
                else:
                    print(f"old path {old_file}")
                    print(f"renamed: {correct_path}")
                    old_file.rename(correct_path)
                    # old_file.unlink()

    def convert_underscore_names(self, files, delete=False):
        """convert pmid_author_year_ to correct format
        (pmid author year.pdf)

        Arg: files = list of files
             delete = bool, where True means Path.unlink() old
             file
        """
        for file in files:
            if re.match(PMID_AUTHOR_YEAR_UNDERSCORE, file):
                old_file = Path(self.directory_path/file)
                file_stem = file.split(".")[0]
                file_stem = file_stem.replace('_', ' ')
                correct_name = file_stem+".pdf"
                correct_path = Path(self.directory_path/correct_name)
                if correct_path.is_file():
                    # check for existing file of same name
                    print(f"file exists {correct_path}")
                    if delete and old_file.is_file():
                        print(f"deleting {old_file}")
                        old_file.unlink()
                    continue
                else:
                    print(f"old path {old_file}")
                    print(f"renamed: {correct_path}")
                    old_file.rename(correct_path)
            else:
                continue


    def remove_dups_with_parentheses(self, files, delete=False):
        """removes files with (digit).pdf at the end, eg.
        16339096 (1).pdf
        """
        for file in files:
            if re.match(PARENTHESES_MATCH, file):
                old_file = Path(self.directory_path/file)
                if delete and old_file.is_file():
                    print(f"deleting {old_file}")
                    old_file.unlink()
                    continue

    @staticmethod
    def copy_file(source_file, dest_file):
        """uses shutil.copyfile to
        copy source_file to dest_file
        """
        print(f"copying {source_file} to {dest_file}")
        shutil.copyfile(source_file, dest_file)

// // // // // // // // // // // // // // // // // // // // // // //
//  COMP2521 20T2 Assignment 1. Text Analytics 
//
//  tw.c ... compute top N most frequent words in file F
//  Usage: ./tw [Nwords] File
//
//  The following links served as inspiration for putting this 
//  assignment together: 
//  <https://stackoverflow.com/questions/757627/how-do-i-align-a-number-like-this-in-c>
//  <https://stackoverflow.com/questions/1258550/why-should-you-use-strncpy-instead-of-strcpy>
//  <https://unix.stackexchange.com/questions/12068/how-to-measure-time-of-program-execution-and-store-that-inside-a-variable>
//  <https://stackoverflow.com/questions/27284185/how-does-the-compare-function-in-qsort-work>
//
//  Big thank you to the staff who put together the week 3 and 4 lab 
//  tasks! The starting code for those tasks, if not found in this 
//  program, have definitely inspired lots of the code. Acknowledgements
//  are written throughout the code.
//
//  Lucas Barbosa (z5259433)
// =================================================================

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>
#include <string.h>
#include <ctype.h>
#include "Dict.h"
#include "WFreq.h"
#include "stemmer.h"

// ------------------------------------------------------------------
// FUNCTION PROTOTYPES
void toLower(char *str);
void removeNewline(char *str);

void addWordToDict(char *word, Dict stopwords, Dict wfreqs);
Dict createStopwordDict();

int main( int argc, char *argv[])
{

   FILE  *in;         // currently open file
   Dict   stopwords;  // dictionary of stopwords
   Dict   wfreqs;     // dictionary of words from book
   WFreq *results;    // array of top N (word,freq) pairs
                      // (dynamically allocated)

   char *fileName;    // name of file containing book text
   int   nWords;      // number of top frequency words to show

   char   line[MAXLINE];  // current input line

   // process command-line args
   switch (argc) {
   case 2:
      nWords = 10;
      fileName = argv[1];
      break;
   case 3:
      nWords = atoi(argv[1]);
      if (nWords < 10) nWords = 10;
      fileName = argv[2];
      break;
   default:
      fprintf(stderr,"Usage: %s [Nwords] File\n", argv[0]);
      exit(EXIT_FAILURE);
   }

   // TODO(1) build stopword dictionary
   stopwords = createStopwordDict();

   // TODO (2) skip to *** START line
   in = fopen(fileName, "r");
   if (in == NULL) {
      fprintf(stderr, "Can't open %s\n", fileName);
      exit(EXIT_FAILURE);
   }

   int validBook = 0;
   memset(line, 0, sizeof(line));
   
   // check if the text file is a valid Gutenburg book
   while (fgets(line, MAXLINE, in) != NULL) {
      if (strstr(line, STARTING) != NULL) {
         validBook = 1;
         break;
      }
   }

   if (validBook == 0) {
      fprintf(stderr, "Not a Project Gutenberg book\n");
      exit(EXIT_FAILURE);
   }

   // jump to the next line of the book (after *** START)
   fgets(line, MAXLINE, in);
   char *nonValidChars = "\\/:;*&#^()[]{}`~,._?!\"\r\n\t ";

   wfreqs = newDict();
   while (strstr(line, ENDING) == NULL) {
      char *insertWord = strtok(line, nonValidChars);
      while (insertWord != NULL) {
         addWordToDict(insertWord, stopwords, wfreqs);
         insertWord = strtok(NULL, nonValidChars);
      }
      // jump to next line
      fgets(line, MAXLINE, in);
   }

   // TODO(4) compute and display the top N words
   results = malloc(sizeof(WFreq)*nWords);
   if (results == NULL) {
      fprintf(stderr, "Can't access memory.\n");
      exit(EXIT_FAILURE);
   }

   int nWordsFound = findTopN(wfreqs, results, nWords);

   // print topN values 
   for (int i = 0; i < nWordsFound; i++) {
      printf("%7d %s\n", results[i].freq, results[i].word);
   }

   // done
   free(results);
   fclose(in);
   return EXIT_SUCCESS;
}

// ------------------------------------------------------------------
// HELPER FUNCTIONS

// creates a stopword dictonary based of the stopwords provided 
// for this assignment. 
Dict createStopwordDict() {
   Dict stopwords = newDict();
   char line[MAXLINE]; 
   FILE *stopwordsFile = fopen(STOPWORDS, "r");
   if (stopwordsFile == NULL) {
      fprintf(stderr, "Can't open stopwords\n");
      exit(EXIT_FAILURE);
   }

   // insert stopwords line by line into a dictionary
   while (fgets(line, MAXLINE, stopwordsFile) != NULL) {
      removeNewline(line);
      DictInsert(stopwords, line); 
   }
   fclose(stopwordsFile);
   return stopwords;
}

// (1) set word to all lower case
// (2) check if word is a stopword
// (3) process word through provided stemmer
// (4) insert into wfreqs dictionary
void addWordToDict(char *word, Dict stopwords, Dict wfreqs) {
   toLower(word); 
   
   if ((DictFind(stopwords, word) == NULL)) {
      int end = stem(word, 0, strlen(word) - 1);
      word[end + 1] = '\0';
      if (strlen(word) > 1) DictInsert(wfreqs, word);
   }
}
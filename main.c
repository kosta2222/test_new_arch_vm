/* 
 * File:   main.c
 * Author: papa
 *
 * Created on 18 апреля 2021 г., 22:25
 */

#include <stdio.h>
#include <stdlib.h>

// base type
typedef struct object{
    int ref_count;
    char *type;
}object;

// derivate int
typedef struct int_obj{
   object ob_base;
   int v;
}int_obj;

// derivate str
typedef struct str_obj{
   object ob_base;
   char * v;
}str_obj;
        

int main(int argc, char** argv) {
    // C subtyping!
    object ** stack=malloc( sizeof(int_obj)+sizeof(str_obj)); // stack of 2 objects
    // alocating 1 object
    int_obj* i=malloc(sizeof(int_obj));
    // initialize 2 object
    str_obj* str=malloc(sizeof(str_obj));
    str->ob_base=(object){1,"<str>"};
    str->v="hi!";
    // assign to 'common' stack
    stack[-1]=str;
    printf(stack[-1]->type); //-> <str>
    // customing 
    printf(((str_obj*)stack[-1])->v);//-> hi!
    return (EXIT_SUCCESS);
}


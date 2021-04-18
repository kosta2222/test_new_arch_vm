/* 
 * File:   main.c
 * Author: papa
 *
 * Created on 18 апреля 2021 г., 22:25
 */

#include <stdio.h>
#include <stdlib.h>

/*
 * 
 */
typedef struct object{
    int ref_count;
    char *type;
}object;

typedef struct int_obj{
   object ob_base;
   int v;
}int_obj;

typedef struct str_obj{
   object ob_base;
   char * v;
}str_obj;

//void print_(object v_){
//    if(strcmp(v_.type,"<int>"))
//        printf("obj %d", v_.v);
//    else if((strcmp(v_.type,"<str>"))
//        printf("obj %s", v_.v);
//}
        

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
    printf(stack[-1]->type);
    // customing 
    printf(((str_obj*)stack[-1])->v);//-> <str>hi!
    return (EXIT_SUCCESS);
}


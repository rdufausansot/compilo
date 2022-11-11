#################   #####   #######   #####     #################
#################   #    #     #      #    #    #################
#################   #####      #      #####     #################
#################   #          #      #   ##    #################
#################   #          #      #     #   #################


################# Manuel d'utilisation compilo_ptr #################

Le compilateur compilo_ptr permet une utilisation basique des pointeurs.


======== Pour la compilation: ========

Le compilo utilise le fichier moule.asm pour écrire le fichier assembleur final, qui est enregistré dans "okk.asm"

Utiliser le makefile donné pour faciliter la compilation, ou copier ces lignes dans un makefile :
~~~~~~~~ makefile: ~~~~~~~~
all: okk_exe

okk_exe: okk.o
    gcc -no-pie -fno-pie okk.o -o okk_exe

okk.o: okk.asm
    nasm -f elf64 okk.asm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Dans ce cas, il faut alors executer `$ ./okk_exe <args>`

=======================================


>>>>>>>>>>>> FEATURES <<<<<<<<<<<<

DISCLAIMER : dans la suite, l'appelation <ptr> ne sécurise pas l'utilisation de pointeur : les pointeurs ne sont pas déclarés ! (ce sont de simples variables)

&<var>                      -> recupère l'adresse d'une variable

*<ptr> = <exp>             -> change la valeur de la variable à l'adresse du pointeur 
<var> = *<ptr>              -> assigne la valeur de la variable pointée

Les doubles pointeurs (seulement) sont autorisés.

*(<ptr> + <entier>)         ou
*(<ptr> - <entier>)         -> pour récupérer ou définir une valeur dans les zones mémoires adjacentes au pointeur [seulement pour des pointeurs simples]

<ptr> = malloc(<entier>)    -> l'argument correspond au nombre de cases mémoires de *8 bytes* à allouer. ptr pointe alors vers la première zone de la mémoire allouée

=================================


[[[[[[[[[[[[ EXEMPLES ]]]]]]]]]]]]

Les exemples des utilisations basiques et types sont dans le fichier 'exemples_ptr.txt', avec les résultats attendus (et obtenus avec la version finale)

(le merge avec le compilateur pour les tableaux n'a malheureusement pas pu avoir lieu, ce qui aurait néanmoins donné de meilleurs exemples d'utilisation du malloc et de l'accès aux zones adjacentes)

==================================
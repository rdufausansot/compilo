################# Manuel d'utilisation compilofloat ##################################


Le compilateur compilofloat permet une utilisation basique des floats.


======== Pour la compilation: ========

Le compilo utilise le fichier moulefloat.asm pour écrire le fichier assembleur final, qui est enregistré dans "ouf.asm"

On entre les lignes suivantes pour utlisier le compilo :

python compilofloat.py
nasm -f -no-pie -fno-pie ouf.o -lm
./a.out <valeur variable1>....


=======================================


>>>>>>>>>>>> FEATURES <<<<<<<<<<<<

Les expressions sont typées dans compilofloat.
Les variables entières sont de la forme : ix, ia ...
Les variables flottantes sont de la forme : fx, fb ...
Si on essaye d'affecter à une variable une expression qui n'est pas de son type, le compilateur convertit l'expression.

Les opérations se finississent toujours par un point virgule.

Les opérations mathématiques disponibles sur compilofloat sont :
	~Multiplication, addition, soustraction : 
		Fonctionnent sur les floats et les entiers.
		Si on veut ajouter une expression flotante et une expression entière, le compilateur convertit l'expression entière en float.
	~opérateur de comparaison > : 
		Fonctionnent sur les entiers et les floats
	~racine carré (noté sqrt(exp)) :
		Fonctionnent sur les entiers et les flottants.
		Il n'y a pas de test du signe de l'expression (lors de mes test, le compilateur envoyait un segmentation fault)   


Les boucles disponibles dont if et while : 
	La syntaxe est : if(exp){ ... } et while(exp){ ... }

Le print fonctionne sur les entiers et les flottants.
	La syntaxe est : print(exp);

La syntaxe d'un programme est : 

main(fx, iy,...){
	commandes
	return exp
}



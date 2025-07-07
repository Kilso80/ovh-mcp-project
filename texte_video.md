Bonjour tout le monde! 
Aujourd'hui, nous allons découvrir comment il est possible de créer un chatbot un peu spécial.
Ce chatbot sera capable non seulement de converser avec l'utilisateur, mais aussi d'effectuer des requêtes dans une base de données pour répondre aux questions qui lui sont posées.
Commençons tout de suite par définir ce que nous allons faire.

Notre objectif, dans cette vidéo sera de créer un agent conversationnel qui utilisera le Model Context Protocol, qu'on appellera le MCP.
Ce protocole lui permettra d'intéragir avec une base de données via des requêtes.
Concernant les technologies que nous allons utiliser, nous allons utiliser une base de données postgreSQL et des scripts python.
Concrètement, le projet que je vais vous présenter est un PoC. 
Nous allons créer une base de données pour une hypothétique application de to-do list, ainsi que son fameux assistant chatbot.
Maintentant que vous connaissez notre objectif, il ne nous reste plus qu'à nous y mettre, donc allons-y !
La première étape de ce projet est simplement de concevoir et de mettre en place la base de données de notre application.
Pour cela, nous allons faire un schéma des informations dont nous avons besoin sur excalidraw.

Commençons par ce qui est évident, nous allons avoir besoin de tâches.
Chacune de ces dernières aura un nom, un id. Il faudra aussi sauvegarder sa date de création et de dernière modification.
Quelque chose d'intéressant serait d'avoir la possibilité de créer des sous-tâches pour découper les choses à faire les plus complexes en quelques tâches bien plus simples.
Pour cela, nous allons ajouter un champ parent, qui référencera l'id de la tâche parente.
Nous allons aussi créer des catégories pour les tâches. Chaque tâche aura donc un champ category_id.
Il est donc maintenant logiquement temps de concevoir la table des catégories.
Chacune d'entre elles aura un id, un nom et une couleur pour son affichage.

Revenons aux tâches. 
Un élément important que nous avons négligé est leur statut.
Effectivement, il est important de savoir si chaque tâche est faite, à faire, ou pourquoi pas en cours d'accomplissement.
Nous allons donc ajouter une table répertoriant les statuts, chacun ayant un id, un nom et une description.
Il faut aussi donc ajouter une référence au statut de chaque tâche dans la table concernée.

Le système d'utilisateurs est aussi une partie importante de l'application.
Il nous faut donc une liste d'utilisateurs.
Chacun d'entre eux aura un identifiant, un nom et un mot de passe dont on stockera le hash.
Afin d'accéder à l'API, un système de tokens sera mis en place. 
Ces tokens seront des chaines de 32 caractères alphanumériques aléatoires.
Chaque token correspondra à un utilisateur, avec une date d'expiration, fixée à une heure après la création du token.

Enfin, il faut relier les utilisateurs à leurs catégories et tâches. 
Pour cela, nous allons créer une table répértoriant les accès.
Cela permettra à plusieurs utilisateurs de travailler en collaboration sur une liste de tâches.
Chaque enregistrement de cette table contiendra l'idantifiant d'un utilisateur, celui d'une catégorie, et le niveau d'accès que l'utilisateur possède sur la catégorie.

En effet, il y aura plusieurs niveaux d'accès.
Commençons par le plus bas. Un utilisateur peut avoir uniquement l'accès en lecture d'une catégorie. Il aura alors le niveau 0.
Juste au dessus, l'utilisateur peut être un acteur dans la liste de tâches sans avoir le droit d'en créer. 
Il aura alors uniquement le droit de modifier le statut des tâches concernées.
Au niveau superieur, l'utilisateur aura le droit de créer, modifier et supprimer des tâches dans la catégorie.
Au suivant, l'utilisateur sera un administrateur. Cela signifie qu'il peut accorder ou révoquer des accès de niveau inferieur au sien pour d'autres utilisateurs.
Enfin, le rôle par défaut de l'utilisateur ayant créé la catégorie est celui de propriétaire, qui a, en plus de tout ça, le droit de gérer les administrateurs. 
C'est aussi le seul ayant le droit de renommer et de supprimer la catégorie.

Nous avons donc un schéma plutôt complet de la base de données.
Plutôt que de l'implémenter à la main, pourquoi ne pas utiliser une IA pour le faire à notre place ?
Il est possible de simplement enregistrer l'image et de l'envoyer à OmisimO, qui saura nous génerer le code SQL pour créer tout ça.

Maintenant, afin de pouvoir faire des tests plus simplement, il nous faudrait des jeux de tests. Pour cette tâche répétitive, quoi de mieux que de demander à l'IA de le faire pour nous ? 
Aifn de faire cela, j'ai simplement evnoyé les requêtes de création de tables SQL à l'IA et lui ai demandé de créer des données de tests.
Pour lui simplifier le travaild, je lui ai demandé de faire cela table par table. 
De cette manière, ne gardant que les réponses me convenant, l'historique de la conversation servait d'example à l'IA pour créer ces requêtes.

Maintenant que la base de données est prête, nous allons pouvoir nous attaquer à la mise en place du chatbot.
Avant de nous y mettre, nous allons faire un petit point concernant le fonctionnement du MCP.
Pour cela, nous allons nous intéresser à ce schéma.
Il nous montre que nous avons besoins de quatre éléments principaux. 
D'un côté, nous avons la base de données, que nous avons déjà créée. 
D'un autre côte, nous avons un utilisateur, qui va poser des questions.
Entre les deux, il y a un LLM et un serveur MCP.
Pour faire simple, le LLM interroge le serveur MCP pour connaître les outils à sa disposition, et utilise ces outils pour répondre à la demande de l'utilisateur.

Nous allons donc continuer en mettant en place le serveur MCP.
Pour faire cela, il existe déjà de nombreux scripts qui le font, et moyennant un peu de débug, il est assez simple de le mettre en place.

Ensuite, j'ai mis en place le LLM, en utilisant le modèle Llama 3. 
Dans ce but, j'ai à nouveau créé un script python. 
Cette fois, ce script est une agglomération de code écrit à la main, généré par une IA et trouvé sur internet.

Maintenant, une fois la connection établie entre le LLM et le serveur MCP, il est temps de tester.
Voulant vérifier que la connection est bien mise en place entre les différents éléments, je demande au chatbot quelles sont les tables auquelles il a accès. 
Cependant, au lieu de me parler de tâches, à chaque fois que je lui demande, il me dit qu'il y a des tables à propos de produits, d'utilisateurs et de commandes.
Au vu de ces réponses, on pourrait avoir l'impression que le chatbot est connecté à une autre base de données, mais en cherchant bien, on se rend compte que ce n'est pas le cas.
En réalité, il n'était simplement connecté à aucune base de données !
Régler ce problème n'est pas bien compliqué, mais ce qui se cache derrière ces réponses surprenantes est bien pire.
Cet autre problème est le pire que nous rencontrerons avec ce chatbot: c'était ce qu'on appelle une hallucination.
Ces hallucinations arrivent lorsque le modèle rencontre une erreur.
Évidemment, en bon assistant, le modèle veut éviter de dire à l'utilisateur qu'il ne peut pas répondre à sa question.
Son comportement est donc un peu étonnant.
Il invente une réponse de toutes parts.

Pour résoudre ce problème, la seule solution à notre disposition est de retravailler le prompt système de l'IA.
La solution la plus efficace que j'ai trouvée dans cette optique est d'ajouter une liste de règles à l'IA dans ses consignes. 
Parmi ces règles, une instruction dit au modèle d'avertir l'utilisateur lorsqu'une erreur est rencontrée, puis de suggérer des solutions avant d'essayer de les appliquer.
Une autre règle impose au modèle d'utiliser ses outils pour vérifier le format des tables de la base de données avant d'écrire des requêtes.
Cependant, notre assistant est plutôt capricieux et ne suit la plupart du temps pas cette instruction.
Cela le mêne à de nombreuses erreurs.
Nous allons régler ce problème de la même manière que le précédent: en modifiant le prompt.
Pour cela, nous récupérons l'export du modèle de la base de données et demandons à une IA de le résumer.
Nous ajoutons simplement son résultat dans une section du prompt système de notre chatbot.

Maintenant, notre chatbot marche plutôt bien ! 
Il est possible de lui poser de nombreuses questions à propos de la base de données est d'obtenir une répoonse correcte.
Cependant, le modèle rencontre ses limites face à des requêtes plus complexes.
En fait, llama 3 n'est pas si bon que ça pour écrire du code, et donc pour faire des requêtes à la base de données.
Pour cette raison, j'ai décidé d'utiliser à partir de maintenant le LLM Qwen 2.5, spécialisé dans la génération de code.
Cela demande quelques adaptations. 
La plus importante est la détection de l'utilisation des outils.
L'avantage de llama est qu'avec ses réponses, il fournit ce qui est appelé une stop reason.
Cette dernière peut nous informer que le modèle s'est arrêté car sa réponse est complète, ou bien (et c'est ce qui nous intéresse ici) parce qu'il attend l'exécution d'un outil.
Avec Qwen, il devient nécessaire de détecter que le modèle essaie d'utiliser l'un de ces outils.
Cela ajoute un peu de complexité, mais une fois que c'est fait, nous arrivons à la version finale de notre chatbot, qui est maintenant capable d'une grande flexibilité pour répondre à nos questions concernant le contenu de la base de données.

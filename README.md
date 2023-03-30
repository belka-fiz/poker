# What's going on here
Hi! This is a single-player console poker game with kind of AI.
I've written this to have some practice in Python development and to have a hand-made game to play with and to help myself to understand poker decision-making better.

## How this works
- There is a deck of cards with suits and values. The cards can be dealt to players, opened on the board, or hidden.
- There are combinations, that can be formed with 2 to 7 cards from High Card to Royal Flush. The combinations can be compared to decide the winner
- There are players.
  - Players have money and two hand cards.
  - They can also see the board cards, but not the other players'.
  - Players can check, call, raise, fold or go all-in.
- There is an AI that can:
  - consider all possible combinations for itself and for its opponents,
  - calculate the chances to win and make a bet according to that.
  - It can also bluff to make its status less predictable just according to the bet.  
- There is the game with rounds that cycle while there are players who can still bet.
- There is a role of Dealer and there are small and big blinds.

### Typical game round:
1. The first player after the Dealer places the small blind bet and the next one places the big blind.
2. The cards are dealt to players starting from the player next to the Dealer.
3. Pre-flop. Each player may make a bet starting from the player after the big blind player. If everyone checks, the big blind player is the last to make a bet.
4. A card from the top of the deck is hidden, and then the flop is played.
5. Flop. Three cards are open. Players start to make their bets starting with the player after the Dealer. People who folded or went all-in can not bet anymore.
6. If there is only one player left, who did not fold, he wins.
7. Turn and River are played similarly to the Flop except that there is only one card added to the board.
8. After all bets are made, the hands of not-folded players become open. The game calculates the best combination and chooses the winner. The draw is also possible.
9. The pot is split between the winners.

## Known issues:
- It takes quite long for AI to calculate chances and make a decision on the Flop stage. AI will be completely overwritten using math. One day and maybe.

## Plans
I'm going to.. 
- Tidy up the structure of the program, separate modules into folders, etc.
- Separate player interface from the game and make AI work through the same interface. This should also help to test the system allowing to emulate players.
- Implement some math to the AI, instead of just looping through all possible cards and combinations. There are some drafts already.
- Improve gaming state machine to make it more testable.
- Implement more unit tests. Ideally - with 90+ % code coverage, but I'll see whether it is possible.
- Make it a client-server app with the core and AI on the server side and human players interface on the client side. This may become a very complicated task due to authentication, session and state storage and other serious staff I've never worked with as a developer.
- Implement API tests for the client-server version. 
- Make some graphics for the client side.

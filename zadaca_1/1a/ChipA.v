Set Implicit Arguments.
Require Import List.
Require Import Bool.
Import ListNotations.

Lemma ChipA (x y: bool) :
  (x && negb(y)) || (negb(x) && negb(y)) || (negb(x) && y) = negb(x && y).
Proof.
  intros. destruct x, y.
  -reflexivity.
  -reflexivity.
  -reflexivity.
  -reflexivity.
Qed.
Set Implicit Arguments.
Require Import List.
Require Import Bool.
Import ListNotations.

Lemma ChipB (x y z: bool) :
  negb(negb(x) && y && z) && negb(x && y && negb(z)) && (x && negb(y) && z) = x && negb(y) && z.
Proof.
  intros. destruct x, y, z.
  -reflexivity.
  -reflexivity.
  -reflexivity.
  -reflexivity.
  -reflexivity.
  -reflexivity.
  -reflexivity.
  -reflexivity.
Qed.
from manimlib import *

from chemanim.chem_object import ChemObject
from chemanim.rdkit_adapter import (
    detect_functional_groups,
    functional_group_palette,
    molecule_data_from_smiles,
)


class MultiStepOxidation(Scene):
    """Mechanism-style, multi-step oxidation: ethanol -> acetaldehyde -> acetic acid."""

    def construct(self):
        title = Text("Multi-step oxidation (alcohol to acid)", font_size=34).to_edge(UP)
        palette = functional_group_palette()

        # Transition annotations (between steps i -> i+1)
        transition_specs = [
            {
                "highlight_atoms": [1, 2],  # alpha carbon and hydroxyl oxygen in ethanol
                "arrows": [
                    {"start": 1, "end": 2, "label": "H abstraction"},
                ],
            },
            {
                "highlight_atoms": [1, 3],  # carbonyl carbon and hydroxyl oxygen in acetic acid (if present)
                "arrows": [
                    {"start": 3, "end": 1, "label": "Further oxidation"},
                ],
            },
        ]

        steps = [
            {
                "smiles": "CCO",  # ethanol
                "label": "Ethanol",
                "note": "Primary alcohol",
                "transition": "Oxidation (loss of H2)",
            },
            {
                "smiles": "CC=O",  # acetaldehyde
                "label": "Acetaldehyde",
                "note": "Aldehyde intermediate",
                "transition": "Oxidation (add O)",
            },
            {
                "smiles": "CC(=O)O",  # acetic acid
                "label": "Acetic acid",
                "note": "Carboxylic acid product",
                "transition": "",
            },
        ]

        cards = []
        for step in steps:
            data = molecule_data_from_smiles(step["smiles"], add_h=False)
            matches = detect_functional_groups(step["smiles"])

            mol = ChemObject(
                data,
                skeletal=True,
                use_external_coords=True,
                skeletal_carbon_marker_radius=0.06,
                skeletal_carbon_marker_color=GREY_C,
                font_size=28,
                bond_stroke=4,
            )
            mol.scale(0.9)
            mol.add_functional_group_highlights(
                matches,
                palette=palette,
                label_font_size=20,
                fill_opacity=0.12,
                stroke_width=3,
                buff=0.6,
                show_labels=True,
            )

            label = Text(step["label"], font_size=26)
            note = Text(step["note"], font_size=20, color=GREY_B)
            caption = VGroup(label, note).arrange(DOWN, aligned_edge=ORIGIN, buff=0.12)

            card = VGroup(mol, caption).arrange(DOWN, buff=0.4)
            cards.append(card)

        if not cards:
            return

        cards[0].move_to(ORIGIN)
        step_label = Text(f"Step 1 of {len(cards)}", font_size=22).next_to(title, DOWN, buff=0.2)

        self.play(Write(title), FadeIn(cards[0]), FadeIn(step_label))
        self.wait(1)

        current = cards[0]
        for idx in range(1, len(cards)):
            nxt = cards[idx]
            nxt.move_to(current.get_center())

            transition_text = steps[idx - 1].get("transition", "")
            arrow_note = None
            if transition_text:
                arrow_note = Text(transition_text, font_size=22, color=YELLOW_D)
                arrow_note.next_to(step_label, DOWN, buff=0.15)
                self.play(Write(arrow_note))

            # Mechanistic overlays on the current structure
            spec = transition_specs[idx - 1] if idx - 1 < len(transition_specs) else {}
            overlays = self._build_transition_overlays(
                current[0],
                spec.get("highlight_atoms", []),
                spec.get("arrows", []),
            )
            if overlays:
                self.play(FadeIn(overlays, lag_ratio=0.1, run_time=0.8))

            new_step_label = Text(f"Step {idx + 1} of {len(cards)}", font_size=22)
            new_step_label.move_to(step_label.get_center())
            self.play(Transform(step_label, new_step_label))
            self.play(
                ReplacementTransform(current, nxt),
                FadeOut(overlays) if overlays else AnimationGroup(),
            )
            current = nxt

            if arrow_note:
                self.play(FadeOut(arrow_note))
            self.wait(0.5)

        self.wait(2)

    def _build_transition_overlays(self, mol: ChemObject, highlight_atoms, arrows):
        overlays = VGroup()

        # Atom highlights
        radius = getattr(mol, "bond_length", 1.5) * 0.55
        for idx in highlight_atoms:
            atom = getattr(mol, "atoms_dict", {}).get(idx)
            if not atom:
                continue
            circ = Circle(
                radius=radius,
                color=YELLOW,
                stroke_width=4,
                fill_opacity=0.15,
                fill_color=YELLOW,
            )
            circ.move_to(atom.get_center())
            overlays.add(circ)

        # Curved arrows for electron-pushing style cues
        for arrow in arrows:
            start_idx = arrow.get("start")
            end_idx = arrow.get("end")
            label_text = arrow.get("label")

            a1 = getattr(mol, "atoms_dict", {}).get(start_idx)
            a2 = getattr(mol, "atoms_dict", {}).get(end_idx)
            if not a1 or not a2:
                continue

            start_pt = a1.get_center()
            end_pt = a2.get_center()
            curved = CurvedArrow(start_pt, end_pt, angle=-PI / 3, color=YELLOW)
            overlays.add(curved)

            if label_text:
                lbl = Text(label_text, font_size=18, color=YELLOW_D)
                lbl.next_to(curved, UP, buff=0.1)
                overlays.add(lbl)

        return overlays

from manimlib import *
from chemanim import Macromolecule
import os


class BioGallery(ThreeDScene):  # ManimGL
    def construct(self):
        # ManimGL camera exposes frame with Euler controls
        self.camera.frame.set_euler_angles(theta=10 * DEGREES, phi=60 * DEGREES)
        self._show_protein_gallery()
        self._show_dna_gallery()

    def _show_label(self, text_obj):
        self.add_fixed_in_frame_mobjects(text_obj)
        return self.play(FadeIn(text_obj))

    def _clear_label(self, text_obj):
        return self.play(FadeOut(text_obj))

    def _show_protein_gallery(self):
        title = Text("Protein: Crambin (1CRN)").to_edge(UP)
        self.add(title)

        try:
            protein = Macromolecule.from_pdb_id("1CRN", render_style="sticks", include_hydrogens=False)
            protein.scale(0.8)
            protein.move_to(ORIGIN)
            self.add(protein)

            # Sticks baseline
            caption = Text("Sticks (default)").to_corner(UL).scale(0.7)
            self._show_label(caption)
            self.play(protein.animate.rotate(1.5 * PI, axis=UP), run_time=4)
            self._snap("protein_sticks")
            self._clear_label(caption)

            # Ribbon with chain colors
            caption = Text("Ribbon (chain-colored)").to_corner(UL).scale(0.7)
            self._show_label(caption)
            protein.apply_render_style("ribbon")
            self.play(protein.animate.rotate(PI, axis=UP), run_time=3)
            self._snap("protein_ribbon")
            self._clear_label(caption)

            # Cartoon (SSE)
            try:
                caption = Text("Cartoon (helix/sheet)").to_corner(UL).scale(0.7)
                self._show_label(caption)
                protein.apply_render_style("cartoon")
                self.play(protein.animate.rotate(PI, axis=UP), run_time=3)
                self._snap("protein_cartoon")
                self._clear_label(caption)
            except ImportError as e:
                warn = Text("Cartoon skipped (install biotite)", color=YELLOW).to_corner(UL).scale(0.6)
                self._show_label(warn)
                self.wait(1.5)
                self._clear_label(warn)

            # Trace lightweight
            caption = Text("Backbone trace").to_corner(UL).scale(0.7)
            self._show_label(caption)
            protein.apply_render_style("trace")
            self.play(protein.animate.rotate(0.5 * PI, axis=UP), run_time=2)
            self._snap("protein_trace")
            self._clear_label(caption)

            self.play(FadeOut(protein), FadeOut(title))

        except Exception as e:
            err = Text(f"Error fetching 1CRN: {e}", color=RED).scale(0.5)
            self.add(err)
            self.wait(2)
            self.remove(err)

    def _show_dna_gallery(self):
        title = Text("DNA: B-DNA (1BNA)").to_edge(UP)
        self.play(FadeIn(title))

        try:
            dna = Macromolecule.from_pdb_id("1BNA", render_style="ball_and_stick", include_hydrogens=False)
            dna.scale(0.8)
            dna.move_to(ORIGIN)
            self.add(dna)

            caption = Text("Ball-and-stick").to_corner(UL).scale(0.7)
            self._show_label(caption)
            self.play(dna.animate.rotate(1.5 * PI, axis=UP), run_time=4)
            self._snap("dna_ball_and_stick")
            self._clear_label(caption)

            caption = Text("Ribbon (sugar-phosphate trace)").to_corner(UL).scale(0.7)
            self._show_label(caption)
            dna.apply_render_style("ribbon")
            self.play(dna.animate.rotate(PI, axis=UP), run_time=3)
            self._snap("dna_ribbon")
            self._clear_label(caption)

            caption = Text("Space filling").to_corner(UL).scale(0.7)
            self._show_label(caption)
            dna.apply_render_style("space_filling")
            self.wait(2)
            self._snap("dna_space_filling")
            self._clear_label(caption)

            self.play(FadeOut(dna), FadeOut(title))

        except Exception as e:
            err = Text(f"Error fetching 1BNA: {e}", color=RED).scale(0.5)
            self.add(err)
            self.wait(2)
            self.remove(err)

    def _snap(self, name: str):
        """Capture the current frame to media/images/bio_gallery."""
        out_dir = os.path.join("media", "images", "bio_gallery")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"{name}.png")
        try:
            img = self.get_image()
            img.save(path)
            print(f"Saved snapshot: {path}")
        except Exception as e:
            print(f"Snapshot failed for {name}: {e}")

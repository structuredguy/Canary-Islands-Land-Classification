# -*- coding: utf-8 -*-
"""
Octopus Learning Breakdown Generator
Extracts and enhances the Octopus 0.4 Learning Overview into two clean,
modular, visually rich Grasshopper definitions:
1. 01_Octopus_Supervised_SVM.gh (Supervised Learning: SVM + ANN with clean canvas coordinates)
2. 02_Octopus_Evolutionary_NEAT.gh (Evolutionary Learning: NEAT topology breeding with clean canvas coordinates)
"""

import os
import clr
clr.AddReference("System.Drawing")
from System.Drawing import PointF, RectangleF
clr.AddReference(r"C:\Program Files\Rhino 8\Plug-ins\Grasshopper\GH_IO.dll")
from GH_IO.Serialization import GH_Archive

SOURCE_GH = r"C:\dev\Canary-Islands-Land-Classification\Tareas\Tarea_4\Octopus 0.4\Manual\Octopus Learning Overview.gh"
OUT_DIR = r"C:\dev\Canary-Islands-Land-Classification\Tareas\Tarea_4"

def shift_canvas_to_origin(def_objs, target_x=100.0, target_y=100.0):
    """Shift all components in def_objs so minimum X and Y start at target."""
    min_x = 999999.0
    min_y = 999999.0
    for i in range(def_objs.Chunks.Count):
        ch = def_objs.Chunks[i]
        obj = ch.FindChunk("Container") if ch.FindChunk("Container") else ch
        att = obj.FindChunk("Attributes")
        if att:
            for it in att.Items:
                if it.Name == "Pivot":
                    min_x = min(min_x, it.InternalData.X)
                    min_y = min(min_y, it.InternalData.Y)
        for it in obj.Items:
            if it.Name == "Ca":
                min_x = min(min_x, it.InternalData.X)
                min_y = min(min_y, it.InternalData.Y)

    if min_x > 900000.0 or min_y > 900000.0:
        return

    dx = min_x - target_x
    dy = min_y - target_y

    for i in range(def_objs.Chunks.Count):
        ch = def_objs.Chunks[i]
        obj = ch.FindChunk("Container") if ch.FindChunk("Container") else ch
        att = obj.FindChunk("Attributes")
        if att:
            pt_to_set = None
            r_to_set = None
            for it in list(att.Items):
                if it.Name == "Pivot":
                    pt = it.InternalData
                    pt_to_set = PointF(pt.X - dx, pt.Y - dy)
                elif it.Name == "Bounds":
                    r = it.InternalData
                    r_to_set = RectangleF(r.X - dx, r.Y - dy, r.Width, r.Height)
            if pt_to_set is not None:
                att.RemoveItem("Pivot")
                att.SetDrawingPointF("Pivot", pt_to_set)
            if r_to_set is not None:
                att.RemoveItem("Bounds")
                att.SetDrawingRectangleF("Bounds", r_to_set)

        # Handle Scribbles which store coordinates directly in obj items
        scribble_pts = {}
        for it in list(obj.Items):
            if it.Name in ["Ca", "Cb", "Cc", "Cd"]:
                pt = it.InternalData
                scribble_pts[it.Name] = PointF(pt.X - dx, pt.Y - dy)
        for name, pt in scribble_pts.items():
            obj.RemoveItem(name)
            obj.SetDrawingPointF(name, pt)


def generate_breakdown():
    # --- 1. SUPERVISED LEARNING (SVM & ANN) ---
    arch_sup = GH_Archive()
    arch_sup.ReadFromFile(SOURCE_GH)
    root_sup = arch_sup.GetRootNode
    def_objs_sup = root_sup.FindChunk("Definition").FindChunk("DefinitionObjects")

    # Keep objects with X < 3500 (SVM and ANN sections)
    to_remove_sup = []
    for i in range(def_objs_sup.Chunks.Count):
        ch = def_objs_sup.Chunks[i]
        obj = ch.FindChunk("Container") if ch.FindChunk("Container") else ch
        pivot_x = 0
        att = obj.FindChunk("Attributes")
        if att:
            for it in att.Items:
                if it.Name == "Pivot":
                    pivot_x = it.InternalData.X
        for it in obj.Items:
            if it.Name == "Ca":
                pivot_x = it.InternalData.X
        if pivot_x >= 3500:
            to_remove_sup.append(ch)

    for ch in to_remove_sup:
        def_objs_sup.RemoveChunk(ch)

    shift_canvas_to_origin(def_objs_sup, 100.0, 100.0)
    out_sup = os.path.join(OUT_DIR, "01_Octopus_Supervised_SVM.gh")
    arch_sup.WriteToFile(out_sup, True, False)
    print(f"Generated {out_sup} ({def_objs_sup.Chunks.Count} components, shifted to (100, 100))")

    # --- 2. EVOLUTIONARY LEARNING (NEAT) ---
    arch_evo = GH_Archive()
    arch_evo.ReadFromFile(SOURCE_GH)
    root_evo = arch_evo.GetRootNode
    def_objs_evo = root_evo.FindChunk("Definition").FindChunk("DefinitionObjects")

    # Keep objects with X >= 3500 (NEAT Breeder section)
    to_remove_evo = []
    for i in range(def_objs_evo.Chunks.Count):
        ch = def_objs_evo.Chunks[i]
        obj = ch.FindChunk("Container") if ch.FindChunk("Container") else ch
        pivot_x = 0
        att = obj.FindChunk("Attributes")
        if att:
            for it in att.Items:
                if it.Name == "Pivot":
                    pivot_x = it.InternalData.X
        for it in obj.Items:
            if it.Name == "Ca":
                pivot_x = it.InternalData.X
        if pivot_x < 3500:
            to_remove_evo.append(ch)

    for ch in to_remove_evo:
        def_objs_evo.RemoveChunk(ch)

    shift_canvas_to_origin(def_objs_evo, 100.0, 100.0)
    out_evo = os.path.join(OUT_DIR, "02_Octopus_Evolutionary_NEAT.gh")
    arch_evo.WriteToFile(out_evo, True, False)
    print(f"Generated {out_evo} ({def_objs_evo.Chunks.Count} components, shifted to (100, 100))")

if __name__ == "__main__":
    generate_breakdown()

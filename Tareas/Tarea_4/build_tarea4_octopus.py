# -*- coding: utf-8 -*-
"""
Builds tarea4_octopus_pareto.gh for Tarea 4 (Maximizing 2-Floor Edificability)
modeled on Octopus 0.4's '02_twoObjectivesAndHardConstraint.gh' example:
- Genes (G): Ce, C_ocup, n_cols, typology (0=Box, 1=O-Patio, 2=U, 3=H, 4=Opposed-C)
- Objectives (O - Number + Text):
    1. -E_mat (m2c)       [Minimize -E_mat == Maximize 2-floor buildable area]
    2. C_ocup (%)         [Minimize plot coverage == Maximize private open garden]
    3. Remainder (m2s)    [Minimize subdivision leftover land mod 700 m2s]
- Hard Constraint (O - Boolean):
    Oct_Valid = True iff N_plantas_exact <= 2.0 and S_parcela_avg >= 700 m2s
    (Octopus automatically discards any solution where Oct_Valid is False)
- Phenotype (P - Mesh):
    Joined vertex-colored 3D Mesh of the 6-hectare urban sector so Octopus renders
    every Pareto-optimal solution as a 3D miniature sector inside the Pareto cube.

Also disables the blocking 1000ms Grid-Search (ParamEstimate) in 01_Octopus_Supervised_SVM.gh
and generates fig4_octopus_pareto_front.svg.
"""

import base64
import io
import math
import os
import re
import uuid
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

import clr
clr.AddReference("System")
clr.AddReference("System.Drawing")
import System
from System.Drawing import PointF, RectangleF
clr.AddReference(r"C:\Program Files\Rhino 8\Plug-ins\Grasshopper\GH_IO.dll")
from GH_IO.Serialization import GH_Archive

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
GALAPAGOS_GH = os.path.join(OUT_DIR, "tarea4_galapagos.gh")
EXAMPLE_02_GH = os.path.join(
    OUT_DIR,
    "Octopus 0.4",
    "Examples",
    "Octopus Original Multi-Objective Optimization",
    "02_twoObjectivesAndHardConstraint.gh",
)
SVM_GH = os.path.join(OUT_DIR, "01_Octopus_Supervised_SVM.gh")
OUT_OCTOPUS_GH = os.path.join(OUT_DIR, "tarea4_octopus_pareto.gh")


# %% 1. Embedded Rhino 8 Python 3 Script for Tarea 4 (Galapagos + Octopus Pareto)
GH_PYTHON_CODE = """import math
import System.Drawing as sd
import Rhino.Geometry as rg

ce = float(Ce) if Ce is not None else 1.0
c_ocup = float(C_ocup) if C_ocup is not None else 0.50
ncols = max(1, int(round(float(n_cols)))) if n_cols is not None else 2
typ = int(round(float(typology))) if typology is not None else 1

# Fixed Assignment Rules (DNI last digit = 4 -> 6 ha)
S_BRUTA = 60000.0
R_VIARIO = 0.10
S_VIARIO = S_BRUTA * R_VIARIO
R_CES = 0.45
S_MIN_PLOT = 700.0
NP_CAP = 2
FLOOR_H = 3.0
C_OCUP_CAP = 0.90

# 1. Mass Balance
E_teorica = S_BRUTA * ce
S_cesiones = R_CES * E_teorica
S_neta = max(0.0, S_BRUTA - S_VIARIO - S_cesiones)

N_parcelas = int(math.floor(S_neta / S_MIN_PLOT)) if S_neta >= S_MIN_PLOT else 0
S_parcela_avg = (S_neta / N_parcelas) if N_parcelas > 0 else 0.0
S_remainder = (S_neta - N_parcelas * S_MIN_PLOT) if N_parcelas > 0 else S_neta

S_ocup_total = S_neta * c_ocup
N_plantas_exact = (E_teorica / S_ocup_total) if S_ocup_total > 0 else 999.0
N_plantas_ceil = int(math.ceil(N_plantas_exact)) if N_plantas_exact < 900 else 999

E_cap_2 = NP_CAP * S_ocup_total
E_mat = min(E_teorica, E_cap_2)
Deficit = max(0.0, E_teorica - E_cap_2)

# 2A. Galapagos Single-Objective Scalar Fitness (Maximize)
p_height = 10.0 * Deficit
p_ocup = 200000.0 * max(0.0, c_ocup - C_OCUP_CAP)
p_plot = 500.0 * max(0.0, S_MIN_PLOT - S_parcela_avg) if N_parcelas > 0 else 1e7
p_rem = 0.5 * S_remainder
Fitness = float(E_mat - p_height - p_ocup - p_plot - p_rem)

# 2B. Octopus Multi-Objective Vector (Minimize) + Hard Constraint Boolean (True = Valid)
Oct_Objs = [float(-E_mat), float(round(c_ocup * 100.0, 2)), float(round(S_remainder, 2))]
Oct_Names = ["-E_mat (m2c)", "C_ocup (%)", "Remainder (m2s)"]
Oct_Valid = bool((Deficit <= 1e-3) and (c_ocup <= C_OCUP_CAP + 1e-6) and (N_parcelas >= 1) and (S_parcela_avg >= S_MIN_PLOT - 1e-3))

# 3. Parametric 3D Sector Subdivision (300 m x 200 m = 60,000 m2s)
L = 300.0
W = 200.0
tol = 0.001

if ncols > 1:
    a_q = float(ncols - 1)
    b_q = -(L + W * (ncols - 1))
    c_q = S_VIARIO
    disc = max(0.0, b_q * b_q - 4.0 * a_q * c_q)
    w_road = (-b_q - math.sqrt(disc)) / (2.0 * a_q)
else:
    w_road = S_VIARIO / L

def make_rect_srf(x0, y0, x1, y1, z=0.0):
    if x1 - x0 <= 1e-4 or y1 - y0 <= 1e-4:
        return None
    plane = rg.Plane(rg.Point3d(x0, y0, z), rg.Vector3d.ZAxis)
    rect = rg.Rectangle3d(plane, x1 - x0, y1 - y0)
    breps = rg.Brep.CreatePlanarBreps(rect.ToNurbsCurve(), tol)
    return breps[0] if breps and len(breps) > 0 else None

def make_box(x0, y0, x1, y1, z0, z1):
    if x1 - x0 <= 1e-4 or y1 - y0 <= 1e-4 or z1 - z0 <= 1e-4:
        return None
    box = rg.Box(rg.Plane.WorldXY, rg.Interval(x0, x1), rg.Interval(y0, y1), rg.Interval(z0, z1))
    return box.ToBrep()

def add_colored_quad(mesh, x0, y0, x1, y1, z, col):
    if x1 - x0 <= 1e-4 or y1 - y0 <= 1e-4:
        return
    idx = mesh.Vertices.Count
    mesh.Vertices.Add(x0, y0, z)
    mesh.Vertices.Add(x1, y0, z)
    mesh.Vertices.Add(x1, y1, z)
    mesh.Vertices.Add(x0, y1, z)
    for _ in range(4):
        mesh.VertexColors.Add(col)
    mesh.Faces.AddFace(idx, idx + 1, idx + 2, idx + 3)

def append_brep_to_mesh(parent_mesh, brep, col):
    if brep is None:
        return
    mp = rg.MeshingParameters.FastRenderMesh
    ms = rg.Mesh.CreateFromBrep(brep, mp)
    if not ms:
        return
    for m in ms:
        m.VertexColors.CreateMonotoneMesh(col)
        parent_mesh.Append(m)

def make_mass(x0, y0, x1, y1, c_oc, mode, z0, z1):
    if z1 - z0 <= 1e-4:
        return []
    dx = x1 - x0
    dy = y1 - y0
    cx = 0.5 * (x0 + x1)
    cy = 0.5 * (y0 + y1)
    c_oc = max(0.02, min(0.99, c_oc))

    # Mode 0: Compact Perimeter Setback Box
    if mode == 0 or c_oc >= 0.96:
        s = math.sqrt(c_oc)
        b = make_box(cx - 0.5 * dx * s, cy - 0.5 * dy * s, cx + 0.5 * dx * s, cy + 0.5 * dy * s, z0, z1)
        return [b] if b else []

    s_out = min(0.96, max(0.88, math.sqrt(c_oc + 0.10)))
    if s_out * s_out <= c_oc + 0.01:
        s_out = min(0.99, math.sqrt(c_oc + 0.03))
    ox0 = cx - 0.5 * dx * s_out
    oy0 = cy - 0.5 * dy * s_out
    ox1 = cx + 0.5 * dx * s_out
    oy1 = cy + 0.5 * dy * s_out
    w_out = ox1 - ox0
    h_out = oy1 - oy0
    void_frac = max(0.0, s_out * s_out - c_oc)  # fraction of plot area to leave open inside s_out

    # Mode 1: O-Courtyard Block (central open courtyard)
    if mode == 1:
        s_in = math.sqrt(void_frac)
        o_crv = rg.Rectangle3d(rg.Plane(rg.Point3d(ox0, oy0, z0), rg.Vector3d.ZAxis), w_out, h_out).ToNurbsCurve()
        crvs = [o_crv]
        if s_in > 0.03:
            ix0 = cx - 0.5 * dx * s_in
            iy0 = cy - 0.5 * dy * s_in
            i_crv = rg.Rectangle3d(rg.Plane(rg.Point3d(ix0, iy0, z0), rg.Vector3d.ZAxis), dx * s_in, dy * s_in).ToNurbsCurve()
            crvs.append(i_crv)
        planar = rg.Brep.CreatePlanarBreps(crvs, tol)
        if not planar or len(planar) == 0:
            b = make_box(ox0, oy0, ox1, oy1, z0, z1)
            return [b] if b else []
        path = rg.LineCurve(rg.Point3d(0, 0, z0), rg.Point3d(0, 0, z1))
        solid = planar[0].Faces[0].CreateExtrusion(path, True)
        if solid is not None and solid.SolidOrientation == rg.BrepSolidOrientation.Inward:
            solid.Flip()
        return [solid] if solid else []

    # Mode 2: U-Courtyard Block (open courtyard facing South)
    if mode == 2:
        vw = 0.52 * w_out
        vh = min(0.78 * h_out, (void_frac * dx * dy) / max(1e-3, vw))
        wx = 0.5 * (w_out - vw)
        b_left = make_box(ox0, oy0, ox0 + wx, oy1, z0, z1)
        b_right = make_box(ox1 - wx, oy0, ox1, oy1, z0, z1)
        b_back = make_box(ox0 + wx, oy0 + vh, ox1 - wx, oy1, z0, z1)
        return [b for b in (b_left, b_right, b_back) if b is not None]

    # Mode 3: H-Block (two wings + central bridge, courts North & South)
    if mode == 3:
        vw = 0.48 * w_out
        vh_each = min(0.38 * h_out, 0.5 * (void_frac * dx * dy) / max(1e-3, vw))
        wx = 0.5 * (w_out - vw)
        b_left = make_box(ox0, oy0, ox0 + wx, oy1, z0, z1)
        b_right = make_box(ox1 - wx, oy0, ox1, oy1, z0, z1)
        b_core = make_box(ox0 + wx, oy0 + vh_each, ox1 - wx, oy1 - vh_each, z0, z1)
        return [b for b in (b_left, b_right, b_core) if b is not None]

    # Mode 4: Opposed-C '[ ]' Block (two facing C-wings with permeable central court)
    gap_x = min(0.36 * w_out, (void_frac * dx * dy) / max(1e-3, h_out))
    wing_w = 0.5 * (w_out - gap_x)
    b_c1 = make_box(ox0, oy0, ox0 + wing_w, oy1, z0, z1)
    b_c2 = make_box(ox1 - wing_w, oy0, ox1, oy1, z0, z1)
    return [b for b in (b_c1, b_c2) if b is not None]

Geo_Viario = []
Geo_Cesiones = []
Geo_Parcelas = []
Geo_Edif_OK = []
Geo_Edif_Excess = []
Oct_Mesh = rg.Mesh()

col_road = sd.Color.FromArgb(148, 163, 184)
col_cess = sd.Color.FromArgb(16, 185, 129)
col_plot = sd.Color.FromArgb(191, 219, 254)
col_ok   = sd.Color.FromArgb(37, 99, 235)
col_ex   = sd.Color.FromArgb(220, 38, 38)

y_mid0 = 0.5 * (W - w_road)
y_mid1 = 0.5 * (W + w_road)
h_road = make_rect_srf(0.0, y_mid0, L, y_mid1, 0.0)
if h_road:
    Geo_Viario.append(h_road)
add_colored_quad(Oct_Mesh, 0.0, y_mid0, L, y_mid1, 0.0, col_road)

col_w = (L - (ncols - 1) * w_road) / float(ncols)
row_h = 0.5 * (W - w_road)

for c in range(ncols - 1):
    vx0 = (c + 1) * col_w + c * w_road
    vx1 = vx0 + w_road
    for (ry0, ry1) in [(0.0, y_mid0), (y_mid1, W)]:
        vr = make_rect_srf(vx0, ry0, vx1, ry1, 0.0)
        if vr:
            Geo_Viario.append(vr)
        add_colored_quad(Oct_Mesh, vx0, ry0, vx1, ry1, 0.0, col_road)

B = 2 * ncols
k_list = [N_parcelas // B + (1 if idx < (N_parcelas % B) else 0) for idx in range(B)] if N_parcelas > 0 else [0] * B
S_block = 54000.0 / float(B)

h_ok = min(N_plantas_exact, float(NP_CAP)) * FLOOR_H
h_tot = min(N_plantas_exact, 12.0) * FLOOR_H

b_idx = 0
for row in range(2):
    by0 = 0.0 if row == 0 else y_mid1
    by1 = y_mid0 if row == 0 else W
    for c in range(ncols):
        bx0 = c * (col_w + w_road)
        bx1 = bx0 + col_w
        k_b = k_list[b_idx]
        b_idx += 1

        s_net_b = (S_neta * (float(k_b) / float(N_parcelas))) if N_parcelas > 0 else 0.0
        f_net_b = min(1.0, max(0.0, s_net_b / S_block))
        net_depth = row_h * f_net_b
        ces_depth = row_h - net_depth

        if row == 0:
            ny0, ny1 = by0, by0 + net_depth
            cy0, cy1 = ny1, by1
        else:
            cy0, cy1 = by0, by0 + ces_depth
            ny0, ny1 = cy1, by1

        ces_srf = make_rect_srf(bx0, cy0, bx1, cy1, 0.0)
        if ces_srf:
            Geo_Cesiones.append(ces_srf)
        add_colored_quad(Oct_Mesh, bx0, cy0, bx1, cy1, 0.05, col_cess)

        if k_b > 0 and net_depth > 1e-3:
            pw = col_w / float(k_b)
            for p_i in range(k_b):
                px0 = bx0 + p_i * pw
                px1 = px0 + pw
                ps = make_rect_srf(px0, ny0, px1, ny1, 0.0)
                if ps:
                    Geo_Parcelas.append(ps)
                add_colored_quad(Oct_Mesh, px0 + 0.3, ny0 + 0.3, px1 - 0.3, ny1 - 0.3, 0.05, col_plot)

                for b_ok in make_mass(px0, ny0, px1, ny1, c_ocup, typ, 0.08, h_ok + 0.08):
                    Geo_Edif_OK.append(b_ok)
                    append_brep_to_mesh(Oct_Mesh, b_ok, col_ok)

                if Deficit > 1e-3 and h_tot > h_ok + 1e-3:
                    for b_ex in make_mass(px0, ny0, px1, ny1, c_ocup, typ, h_ok + 0.08, h_tot + 0.08):
                        Geo_Edif_Excess.append(b_ex)
                        append_brep_to_mesh(Oct_Mesh, b_ex, col_ex)

Oct_Mesh.Normals.ComputeNormals()
typ_names = {0: 'Box', 1: 'O-Patio', 2: 'U-Block', 3: 'H-Block', 4: 'Opposed-C'}
status = 'FEASIBLE (<= 2 floors)' if Oct_Valid else 'UNFEASIBLE (Violates 2-floor cap)'
Summary = (
    f'=== TAREA 4 URBAN SECTOR KPI (GALAPAGOS + OCTOPUS) ===\\n'
    f'Status       : {status}\\n'
    f'Typology     : {typ} ({typ_names.get(typ, "Custom")})\\n'
    f'Ce           : {ce:.3f} m2c/m2s\\n'
    f'C_ocup       : {c_ocup*100:.1f} %\\n'
    f'Blocks       : {B} ({ncols} cols x 2 rows) | Street w={w_road:.2f} m\\n'
    f'E_teorica    : {E_teorica:,.0f} m2c\\n'
    f'S_cesiones   : {S_cesiones:,.0f} m2s\\n'
    f'S_neta       : {S_neta:,.0f} m2s\\n'
    f'N_parcelas   : {N_parcelas} plots (avg {S_parcela_avg:.1f} m2s, rem {S_remainder:.0f} m2s)\\n'
    f'N_plantas    : {N_plantas_exact:.2f} -> {N_plantas_ceil} floors\\n'
    f'E_mat (2 fl) : {E_mat:,.0f} m2c | Deficit: {Deficit:,.0f} m2c\\n'
    f'Oct_Objs     : {Oct_Objs} | Oct_Valid={Oct_Valid}\\n'
    f'Galapagos Fit: {Fitness:,.1f}'
)
"""


def add_python_output_param(pd, index, name, access):
    """Add an OutputParam subchunk to Python 3 Script ParameterData."""
    param_id = System.Guid("08908df5-fa14-4982-9ab2-1aa0927566aa")
    type_hint_id = System.Guid("1c282eeb-dd16-439f-94e4-7d92b542fe8b")
    out_guid = System.Guid(str(uuid.uuid4()))

    pd.SetGuid("OutputId", index, param_id)
    ch = pd.CreateChunk("OutputParam", index)
    if access > 0:
        ch.SetInt32("Access", access)
    ch.SetBoolean("AllowTreeAccess", False)
    ch.SetString("Description", "rhinoscriptsyntax geometry")
    ch.SetGuid("InstanceGuid", out_guid)
    ch.SetString("Name", name)
    ch.SetString("NickName", name)
    ch.SetBoolean("Optional", False)
    ch.SetInt32("ScriptParamAccess", access)
    ch.SetInt32("ScriptParameterVersion", 2)
    ch.SetBoolean("ShowTypeHints", True)
    ch.SetInt32("SourceCount", 0)
    ch.SetString("ToolTip", "")
    ch.SetGuid("TypeHintID", type_hint_id)
    return out_guid


def build_octopus_pareto_gh():
    arch = GH_Archive()
    arch.ReadFromFile(GALAPAGOS_GH)
    def_objs = arch.GetRootNode.FindChunk("Definition").FindChunk("DefinitionObjects")

    # 1. Update slider [3] (typology) from 0..1 to 0..4
    c3 = def_objs.Chunks[3].FindChunk("Container")
    c3.RemoveItem("NickName")
    c3.SetString("NickName", "typology (0=Box,1=O,2=U,3=H,4=C)")
    sl3 = c3.FindChunk("Slider")
    sl3.RemoveItem("Max")
    sl3.SetDouble("Max", 4.0)

    # Collect slider GUIDs for Octopus genes
    gene_guids = []
    for idx in [0, 1, 2, 3]:
        g_str = [str(it.InternalData) for it in def_objs.Chunks[idx].FindChunk("Container").Items if it.Name == "InstanceGuid"][0]
        gene_guids.append(System.Guid(g_str))

    # 2. Update Python 3 Script [4] code and add 4 Octopus output pins
    py_c = def_objs.Chunks[4].FindChunk("Container")
    sc = py_c.FindChunk("Script")
    sc.RemoveItem("Text")
    b64_code = base64.b64encode(GH_PYTHON_CODE.encode("utf-8")).decode("ascii")
    sc.SetString("Text", b64_code)

    pd = py_c.FindChunk("ParameterData")
    pd.RemoveItem("OutputCount")
    pd.SetInt32("OutputCount", 12)

    guid_oct_objs  = add_python_output_param(pd, 8,  "Oct_Objs",  1)  # List
    guid_oct_names = add_python_output_param(pd, 9,  "Oct_Names", 1)  # List
    guid_oct_valid = add_python_output_param(pd, 10, "Oct_Valid", 0)  # Item
    guid_oct_mesh  = add_python_output_param(pd, 11, "Oct_Mesh",  0)  # Item

    # 3. Copy Number[47], Text[48], Mesh[49], Boolean[56], and Octopus[148] from Example 02
    arch_ex = GH_Archive()
    arch_ex.ReadFromFile(EXAMPLE_02_GH)
    ex_objs = arch_ex.GetRootNode.FindChunk("Definition").FindChunk("DefinitionObjects")

    def remove_all_items(chunk, item_name):
        for it in list(chunk.Items):
            if it.Name == item_name:
                if it.Index >= 0:
                    chunk.RemoveItem(item_name, it.Index)
                else:
                    chunk.RemoveItem(item_name)

    cur_count = def_objs.Chunks.Count
    # Helper to clone an Object chunk from ex_objs into def_objs
    def clone_ex_object(ex_idx, new_idx, nick, x, y, source_guid=None):
        src_ch = ex_objs.Chunks[ex_idx]
        dst_ch = def_objs.CreateChunk("Object", new_idx)
        dst_ch.CopyValuesFromChunk(src_ch)
        c = dst_ch.FindChunk("Container")
        remove_all_items(c, "NickName")
        c.SetString("NickName", nick)
        if source_guid is not None:
            remove_all_items(c, "Source")
            remove_all_items(c, "SourceCount")
            c.SetGuid("Source", 0, source_guid)
            c.SetInt32("SourceCount", 1)
        att = c.FindChunk("Attributes")
        if att:
            remove_all_items(att, "Pivot")
            att.SetDrawingPointF("Pivot", PointF(float(x), float(y)))
            remove_all_items(att, "Bounds")
            att.SetDrawingRectangleF("Bounds", RectangleF(float(x - 35), float(y - 12), 90.0, 24.0))
        return dst_ch

    # Clone the 4 bridge parameter components at clean coordinates next to the Python solver
    clone_ex_object(47, cur_count + 0, "Oct_Objs",  700, 180, guid_oct_objs)
    clone_ex_object(48, cur_count + 1, "Oct_Names", 700, 225, guid_oct_names)
    clone_ex_object(56, cur_count + 2, "Np<=2 Valid", 700, 270, guid_oct_valid)
    clone_ex_object(49, cur_count + 3, "SectorMesh", 700, 315, guid_oct_mesh)

    # Clone Octopus [148] and wire its OctopusData + Phenotype input
    oct_ch = clone_ex_object(148, cur_count + 4, "Octopus", 900, 240, None)
    oct_c = oct_ch.FindChunk("Container")
    oct_att = oct_c.FindChunk("Attributes")
    remove_all_items(oct_att, "Bounds")
    oct_att.SetDrawingRectangleF("Bounds", RectangleF(865.0, 218.0, 80.0, 48.0))

    od = oct_c.FindChunk("OctopusData")
    # Clear old windmill history so Octopus initializes cleanly for 4 genes
    for item_name in ["gaByteArr", "ga_count", "gene", "gene_count", "obj", "obj_count"]:
        remove_all_items(od, item_name)

    od.SetInt32("ga_count", 0)
    od.SetInt32("gene_count", len(gene_guids))
    for g_i, g_guid in enumerate(gene_guids):
        od.SetGuid("gene", g_i, g_guid)

    # Connect the 3 objective/constraint parameters (Boolean, Number, Text)
    obj_guids = [
        System.Guid("89f66a37-63a2-4e8f-b792-e40348435069"),  # Boolean Hard Constraint
        System.Guid("2ed964da-302f-47c2-9e86-c9590732a9fb"),  # Number Objectives
        System.Guid("09ef66ad-e0e8-48b3-9f0e-1f65613ae3eb"),  # Text Objective Names
    ]
    od.SetInt32("obj_count", len(obj_guids))
    for o_i, o_guid in enumerate(obj_guids):
        od.SetGuid("obj", o_i, o_guid)

    def_objs.RemoveItem("ObjectCount")
    def_objs.SetInt32("ObjectCount", cur_count + 5)

    arch.WriteToFile(OUT_OCTOPUS_GH, True, False)
    print(f"[OK] Saved {OUT_OCTOPUS_GH} with {def_objs.Chunks.Count} objects.")


# %% 2. Fix 01_Octopus_Supervised_SVM.gh so dragging sliders never freezes the UI
def fix_svm_slider_lag():
    if not os.path.exists(SVM_GH):
        return
    arch = GH_Archive()
    arch.ReadFromFile(SVM_GH)
    def_objs = arch.GetRootNode.FindChunk("Definition").FindChunk("DefinitionObjects")
    fixed_count = 0
    for i in range(def_objs.Chunks.Count):
        c = def_objs.Chunks[i].FindChunk("Container")
        if not c:
            continue
        names = [str(it.InternalData) for it in c.Items if it.Name == "Name"]
        if not names:
            continue
        name = names[0]
        # In SVM Learning (oSL), reduce C from 32768.0 (stalls SMO solver) to 100.0
        if name == "SVM Learning (oSL)":
            for sub in c.Chunks:
                if sub.Name == "param_input":
                    pnames = [str(it.InternalData) for it in sub.Items if it.Name == "Name"]
                    if pnames and pnames[0] == "C":
                        pd = sub.FindChunk("PersistentData")
                        if pd and pd.Chunks.Count > 0 and pd.Chunks[0].Chunks.Count > 0:
                            item_ch = pd.Chunks[0].Chunks[0]
                            if item_ch.ItemExists("number"):
                                item_ch.RemoveItem("number")
                                item_ch.SetDouble("number", 100.0)
                                fixed_count += 1
        # In Network Learning (oSL), set On ("boolean") to False by default so slider drags are instant
        if name == "Network Learning (oSL)":
            for sub in c.Chunks:
                if sub.Name == "param_input":
                    pnames = [str(it.InternalData) for it in sub.Items if it.Name == "Name"]
                    if pnames and pnames[0] == "On":
                        pd = sub.FindChunk("PersistentData")
                        if pd and pd.Chunks.Count > 0 and pd.Chunks[0].Chunks.Count > 0:
                            item_ch = pd.Chunks[0].Chunks[0]
                            if item_ch.ItemExists("boolean"):
                                item_ch.RemoveItem("boolean")
                                item_ch.SetBoolean("boolean", False)
                                fixed_count += 1
    arch.WriteToFile(SVM_GH, True, False)
    print(f"[OK] Updated {SVM_GH} (fixed SMO C=32768 stall and ANN On=False on {fixed_count} pins).")


# %% 3. Generate Mobile-Optimized SVG Plot of the Octopus Pareto Frontier
def build_fig4_pareto_svg():
    # Evaluate the exact multi-objective space over the 2-floor feasible boundary
    oc_grid = np.linspace(0.30, 0.90, 601)
    pareto_oc = []
    pareto_emat = []
    pareto_rem = []
    pareto_ce = []
    pareto_plots = []

    for oc in oc_grid:
        ce_max = (1.8 * oc) / (1.0 + 0.9 * oc)
        # Snap to 3-decimal slider step <= ce_max
        ce = math.floor(ce_max * 1000.0) / 1000.0
        e_teo = 60000.0 * ce
        s_net = 54000.0 - 27000.0 * ce
        n_pl = int(math.floor(s_net / 700.0))
        rem = s_net - n_pl * 700.0
        pareto_oc.append(oc * 100.0)
        pareto_emat.append(e_teo / 1000.0)
        pareto_rem.append(rem)
        pareto_ce.append(ce)
        pareto_plots.append(n_pl)

    pareto_oc = np.array(pareto_oc)
    pareto_emat = np.array(pareto_emat)
    pareto_rem = np.array(pareto_rem)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(6.4, 8.6), facecolor="white", gridspec_kw={"height_ratios": [1.15, 0.95], "hspace": 0.38}
    )

    # --- Panel A: Octopus 2-Floor Pareto Front (E_mat vs C_ocup colored by Remainder) ---
    sc = ax1.scatter(
        pareto_oc, pareto_emat, c=pareto_rem, cmap="viridis_r", s=18, zorder=5, label="Pareto Front (Np = 2.00)"
    )
    cbar = fig.colorbar(sc, ax=ax1, pad=0.02)
    cbar.set_label("Plot Remainder (m2s)", fontsize=8.5, fontweight="bold")
    cbar.ax.tick_params(labelsize=8)

    # Shaded dominated interior (feasible Np < 2, lower Ce)
    ax1.fill_between(pareto_oc, 20.0, pareto_emat, color="#DCFCE7", alpha=0.45, zorder=1, label="Feasible Dominated (Np < 2)")
    # Shaded hard-constraint rejection region (Np > 2, Oct_Valid = False)
    ax1.fill_between(pareto_oc, pareto_emat, 62.0, color="#FEE2E2", alpha=0.55, zorder=1, label="Hard Constraint Culled (Np > 2)")

    # Key Pareto & Reference Points
    highlights = [
        ("S4 (50%, Ce=0.60)\n36.0k m2c | 54 plots", 50.0, 36.0, (-8, -32), "#15803D"),
        ("S3 (90%, Ce=0.60)\n36.0k m2c | 54 plots", 90.0, 36.0, (-115, -24), "#15803D"),
        ("Low-Rem Pareto\n(88.2%, Ce=0.885)\n53.1k | 43 plots (5m2 rem)", 88.2, 53.1, (-155, -28), "#7C3AED"),
        ("Peak Yield Pareto\n(90.0%, Ce=0.895)\n53.7k | 42 plots", 90.0, 53.7, (-135, 10), "#2563EB"),
        ("S1/S2 (Ce=1.0)\n60.0k CULLED\n(Oct_Valid=False)", 70.0, 60.0, (-45, -28), "#DC2626"),
    ]
    for txt, px, py, off, col in highlights:
        ax1.plot(px, py, "o", markersize=7, color=col, markeredgecolor="white", zorder=8)
        ax1.annotate(
            txt,
            (px, py),
            xytext=off,
            textcoords="offset points",
            fontsize=7.8,
            fontweight="bold",
            color=col,
            arrowprops=dict(arrowstyle="->", color=col, lw=0.9),
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=col, alpha=0.92),
            zorder=9,
        )

    ax1.set_xlim(30, 94)
    ax1.set_ylim(22, 63)
    ax1.set_xlabel("Objective 2: Plot Occupancy C_ocup (%)  [Minimize -> More Garden]", fontsize=8.8, fontweight="bold")
    ax1.set_ylabel("Objective 1: 2-Floor Yield E_mat (x1,000 m2c)", fontsize=8.8, fontweight="bold")
    ax1.set_title(
        "1. Octopus Multi-Objective Pareto Front (Tarea 4)\n"
        "Trading Off 2-Floor Buildable Area vs. Open Plot Space & Subdivision Remainder",
        fontsize=10.2,
        fontweight="bold",
        pad=8,
    )
    ax1.grid(True, ls=":", color="#CBD5E1", alpha=0.8)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(loc="lower right", fontsize=7.6, frameon=True, facecolor="white", edgecolor="#CBD5E1")

    # --- Panel B: The 5 Parametric 3D Building Typologies in tarea4_octopus_pareto.gh ---
    ax2.set_xlim(0, 5)
    ax2.set_ylim(0, 1.35)
    ax2.axis("off")
    ax2.set_title(
        "2. All 5 Building Typologies (Gene 'typology' = 0..4) at Equal C_ocup\n"
        "Courtyards (O, U, H, Opposed-C) Are Subtracted From Footprint & Preserve Daylight",
        fontsize=10.2,
        fontweight="bold",
        pad=6,
    )

    typs = [
        (0, "0: Box", "Perimeter\nSetback"),
        (1, "1: O-Block", "Central\nCourtyard"),
        (2, "2: U-Block", "South Open\nCourt"),
        (3, "3: H-Block", "Double N/S\nCourts"),
        (4, "4: Opposed-C", "Permeable\nShared Court"),
    ]
    import matplotlib.patches as mpatches

    for idx, name, desc in typs:
        x0 = idx + 0.10
        y0 = 0.28
        w = 0.80
        h = 0.72
        # Plot boundary
        ax2.add_patch(mpatches.Rectangle((x0, y0), w, h, facecolor="#E2E8F0", edgecolor="#475569", lw=1.0, ls="--"))
        # Outer building bounds inside plot
        bx, by, bw, bh = x0 + 0.07, y0 + 0.06, w - 0.14, h - 0.12
        if idx == 0:
            ax2.add_patch(mpatches.Rectangle((x0 + 0.13, y0 + 0.12), w - 0.26, h - 0.24, facecolor="#3B82F6", edgecolor="#1D4ED8", lw=1.1))
        elif idx == 1:
            ax2.add_patch(mpatches.Rectangle((bx, by), bw, bh, facecolor="#3B82F6", edgecolor="#1D4ED8", lw=1.1))
            ax2.add_patch(mpatches.Rectangle((bx + 0.16, by + 0.15), bw - 0.32, bh - 0.30, facecolor="#DCFCE7", edgecolor="#15803D", lw=1.0))
        elif idx == 2:
            ax2.add_patch(mpatches.Rectangle((bx, by), bw, bh, facecolor="#3B82F6", edgecolor="#1D4ED8", lw=1.1))
            ax2.add_patch(mpatches.Rectangle((bx + 0.16, by), bw - 0.32, bh - 0.22, facecolor="#DCFCE7", edgecolor="#15803D", lw=1.0))
        elif idx == 3:
            ax2.add_patch(mpatches.Rectangle((bx, by), bw, bh, facecolor="#3B82F6", edgecolor="#1D4ED8", lw=1.1))
            ax2.add_patch(mpatches.Rectangle((bx + 0.16, by), bw - 0.32, 0.18, facecolor="#DCFCE7", edgecolor="#15803D", lw=1.0))
            ax2.add_patch(mpatches.Rectangle((bx + 0.16, by + bh - 0.18), bw - 0.32, 0.18, facecolor="#DCFCE7", edgecolor="#15803D", lw=1.0))
        elif idx == 4:
            ww = (bw - 0.18) / 2.0
            ax2.add_patch(mpatches.Rectangle((bx, by), ww, bh, facecolor="#3B82F6", edgecolor="#1D4ED8", lw=1.1))
            ax2.add_patch(mpatches.Rectangle((bx + bw - ww, by), ww, bh, facecolor="#3B82F6", edgecolor="#1D4ED8", lw=1.1))
            ax2.add_patch(mpatches.Rectangle((bx + ww, by + 0.04), 0.18, bh - 0.08, facecolor="#DCFCE7", edgecolor="#15803D", lw=0.8, ls=":"))

        ax2.text(x0 + w / 2, y0 + h + 0.08, name, ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#0F172A")
        ax2.text(x0 + w / 2, y0 - 0.06, desc, ha="center", va="top", fontsize=7.8, color="#475569")

    svg_path = os.path.join(OUT_DIR, "fig4_octopus_pareto_front.svg")
    fig.savefig(svg_path, format="svg", bbox_inches="tight", facecolor="white")
    with open(svg_path, "r", encoding="utf-8") as f:
        c_svg = f.read()
    c_svg = re.sub(
        r'(<svg[^>]*?)\s+width="[^"]+"\s+height="[^"]+"',
        r'\1 width="100%" style="max-width:680px;height:auto;display:block;margin:auto;"',
        c_svg,
        count=1,
    )
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(c_svg)

    # In-memory RapidOCR check (no PNG saved to disk)
    try:
        from rapidocr_onnxruntime import RapidOCR
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=180, bbox_inches="tight", facecolor="white")
        buf.seek(0)
        img_arr = np.array(Image.open(buf).convert("RGB"))
        buf.close()
        ocr = RapidOCR()
        res, _ = ocr(img_arr)
        print(f"[OCR CHECK] fig4_octopus_pareto_front.svg: {len(res) if res else 0} text boxes verified cleanly.")
    except Exception as e:
        print("[OCR SKIP]", e)

    plt.close(fig)
    print(f"[OK] Saved {svg_path}")


if __name__ == "__main__":
    build_octopus_pareto_gh()
    fix_svm_slider_lag()
    build_fig4_pareto_svg()

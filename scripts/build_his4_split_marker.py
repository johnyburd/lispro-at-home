#!/usr/bin/env -S uv run --script
#
# /// script
# dependencies = [
#   "biopython",
# ]
# ///

"""Build HIS4 split-marker fragments for making PN-2 Δhis4 auxotrophic.

Strategy
--------
  - LEFT fragment:  [HIS4 upstream arm] + [lox71] + [ILV5] + [EM72] + [NATr 5']
  - RIGHT fragment: [overlap: ILV5' + EM72 + NATr 5'] + [NATr 3'] + [TEF term]
                    + [lox66] + [HIS4 downstream arm]
"""

import os

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_SEQ = f"{ROOT}/PhaffiiNet/data/sequence_resources"
LEFT_SRC = f"{SRC_SEQ}/Phaffiinet_2/hoc1tr_left_split_marker_fragment.gb"
RIGHT_SRC = f"{SRC_SEQ}/Phaffiinet_2/hoc1tr_right_split_marker_fragment.gb"
GENOME_GBK = f"{SRC_SEQ}/Phaffiinet_1/YB-4290_annotated.gbk"
OUT_DIR = "."

ARM_LEN = 1000

GENOME_RECORD_ID = "FN392319.1"
HIS4_REGION_START_1B = 1696356   # inclusive
HIS4_REGION_END_1B = 1701887     # inclusive
HIS4_CDS_START_1B_GENOME = 1697856  # inclusive (PAS_chr1-4_0160)
HIS4_CDS_END_1B_GENOME = 1700387    # inclusive
FLANK = 1500

# Within the extracted region the HIS4 CDS sits at 1-based 1501..4032 (= FLANK+1 .. FLANK + gene_length).
HIS4_CDS_START_1B = FLANK + 1          # 1501
HIS4_CDS_END_1B = FLANK + (HIS4_CDS_END_1B_GENOME - HIS4_CDS_START_1B_GENOME + 1)  # 4032



def load(path):
    return next(SeqIO.parse(path, "genbank"))


def load_his4_region():
    """Extract the HIS4 locus (1.5 kb flanks + CDS) from the YB-4290 genome.

    Returns a SeqRecord with a 5532 bp slice of chromosome FN392319.1 centered on HIS4 (PAS_chr1-4_0160).
    """
    with open(GENOME_GBK) as fh:
        for rec in SeqIO.parse(fh, "genbank"):
            if rec.id == GENOME_RECORD_ID:
                genome = rec
                break
        else:
            raise FileNotFoundError(
                f"record {GENOME_RECORD_ID!r} not found in {GENOME_GBK}"
            )
    start0 = HIS4_REGION_START_1B - 1
    end0 = HIS4_REGION_END_1B  # 0-based exclusive == 1-based inclusive end
    sub = genome.seq[start0:end0]
    if len(sub) != FLANK * 2 + (
        HIS4_CDS_END_1B_GENOME - HIS4_CDS_START_1B_GENOME + 1
    ):
        raise AssertionError(f"unexpected HIS4 region length: {len(sub)}")
    # Sanity-check that the genome's PAS_chr1-4_0160 gene feature lands where expected
    his4_feats = [
        f for f in genome.features
        if f.qualifiers.get("locus_tag", [""])[0] == "PAS_chr1-4_0160"
    ]
    if not his4_feats:
        raise AssertionError("PAS_chr1-4_0160 gene feature not found in genome")
    gf = his4_feats[0]
    if int(gf.location.start) + 1 != HIS4_CDS_START_1B_GENOME or int(
        gf.location.end
    ) != HIS4_CDS_END_1B_GENOME:
        raise AssertionError(
            f"PAS_chr1-4_0160 has moved in the genome annotation: "
            f"found {int(gf.location.start) + 1}..{int(gf.location.end)}, "
            f"expected {HIS4_CDS_START_1B_GENOME}..{HIS4_CDS_END_1B_GENOME}"
        )
    his4_rec = SeqRecord(
        sub,
        id="his4_region_YB4290",
        name="his4_region",
        description="YB-4290 HIS4 locus with 1.5kb flanks (extracted from "
                    f"{GENOME_RECORD_ID} {HIS4_REGION_START_1B}.."
                    f"{HIS4_REGION_END_1B})",
    )
    his4_rec.annotations["molecule_type"] = "DNA"
    return his4_rec


def subseq(rec, start, end):
    """Return rec.seq[start:end] (0-based, end-exclusive)."""
    return rec.seq[start:end]


def make_feature(start, end, label, ftype="misc_feature", strand=1):
    return SeqFeature(
        location=FeatureLocation(start, end, strand=strand),
        type=ftype,
        qualifiers={"label": [label]},
    )


def build_left_fragment(his4_rec, hoc1tr_left):
    """LEFT = HIS4 upstream arm + lox71 + ILV5 + EM72 + NATr 5' portion.

    In hoc1tr_left the cassette runs from the lox71 site (1018..1052) through
    the end of the fragment (1999).
    """
    # HIS4 upstream arm: the ARM_LEN bp immediately 5' of the CDS.
    # CDS starts at 1-based 1501 => 0-based 1500.
    up_start = (HIS4_CDS_START_1B - 1) - ARM_LEN
    up_end = HIS4_CDS_START_1B - 1
    arm = subseq(his4_rec, up_start, up_end)

    # Cassette block from hoc1tr_left: lox71 through NATr 5' (positions
    # 1018..1999 in the original file, 0-based slice [1018:1999]).
    cassette = subseq(hoc1tr_left, 1018, 1999)

    seq = arm + cassette
    rec = SeqRecord(seq, id="his4_left_split_marker", name="his4_left",
                    description="HIS4 left split-marker fragment (delta-his4 donor)")
    rec.annotations["molecule_type"] = "DNA"
    rec.annotations["topology"] = "linear"
    # Annotate features (0-based on the new record).
    arm_off = 0
    cas_off = len(arm)
    rec.features = [
        make_feature(arm_off, arm_off + len(arm), "HIS4 upstream homology arm",
                     ftype="source"),
        make_feature(cas_off + 0, cas_off + 34, "lox71", ftype="protein_bind",
                     strand=-1),
        make_feature(cas_off + 34, cas_off + 34 + 557, "ILV5 promoter",
                     ftype="promoter"),
        make_feature(cas_off + 34 + 557, cas_off + 34 + 557 + 64,
                     "EM72 synthetic promoter", ftype="promoter"),
        make_feature(cas_off + 34 + 557 + 64, cas_off + len(cassette),
                     "NATr", ftype="CDS"),
        make_feature(cas_off + (494 - 0), cas_off + len(cassette),
                     "Overlap between fragments", ftype="misc_feature"),
    ]
    # The overlap region in hoc1tr_left was 1505..1999 (494 bp). In our new
    # record the cassette starts at cas_off (= 1018 in original), so the
    # overlap starts at cas_off + (1505 - 1018) = cas_off + 487.
    rec.features[-1] = make_feature(
        cas_off + (1505 - 1018), cas_off + len(cassette),
        "Overlap between fragments", ftype="misc_feature",
    )
    return rec


def build_right_fragment(his4_rec, hoc1tr_right):
    """RIGHT = overlap + NATr 3' + TEF term + lox66 + HIS4 downstream arm.

    In hoc1tr_right the cassette runs from the start (0) through the lox66
    site (947..981). We take that whole cassette block verbatim and append
    the HIS4 downstream arm.
    """
    # Cassette block from hoc1tr_right: overlap + NATr 3' + TEF + lox66
    # (positions 0..981 in the original file, 0-based slice [0:981]).
    cassette = subseq(hoc1tr_right, 0, 981)

    # HIS4 downstream arm: the ARM_LEN bp immediately 3' of the CDS.
    # CDS ends at 1-based 4032 => 0-based end 4032.
    down_start = HIS4_CDS_END_1B  # 0-based start of downstream flank
    down_end = down_start + ARM_LEN
    arm = subseq(his4_rec, down_start, down_end)

    seq = cassette + arm
    rec = SeqRecord(seq, id="his4_right_split_marker", name="his4_right",
                    description="HIS4 right split-marker fragment (delta-his4 donor)")
    rec.annotations["molecule_type"] = "DNA"
    rec.annotations["topology"] = "linear"
    cas_off = 0
    arm_off = len(cassette)
    rec.features = [
        make_feature(cas_off + 0, cas_off + 494, "Overlap between fragments",
                     ftype="misc_feature"),
        make_feature(cas_off + 0, cas_off + 104, "ILV5 promoter (partial)",
                     ftype="promoter"),
        make_feature(cas_off + 104, cas_off + 104 + 64, "EM72 synthetic promoter",
                     ftype="promoter"),
        make_feature(cas_off + 169, cas_off + 742, "NATr", ftype="CDS"),
        make_feature(cas_off + 749, cas_off + 947, "TEF terminator",
                     ftype="terminator"),
        make_feature(cas_off + 947, cas_off + 981, "lox66",
                     ftype="protein_bind", strand=-1),
        make_feature(arm_off, arm_off + len(arm),
                     "HIS4 downstream homology arm", ftype="source"),
    ]
    return rec


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    his4_rec = load_his4_region()
    hoc1tr_left = load(LEFT_SRC)
    hoc1tr_right = load(RIGHT_SRC)

    left = build_left_fragment(his4_rec, hoc1tr_left)
    right = build_right_fragment(his4_rec, hoc1tr_right)

    left_path = os.path.join(OUT_DIR, "his4_left_split_marker_fragment.gb")
    right_path = os.path.join(OUT_DIR, "his4_right_split_marker_fragment.gb")
    SeqIO.write(left, left_path, "genbank")
    SeqIO.write(right, right_path, "genbank")

    his4_seq = str(his4_rec.seq)
    left_arm = str(left.seq[:ARM_LEN])
    right_arm = str(right.seq[len(right.seq) - ARM_LEN:])
    assert left_arm in his4_seq
    assert right_arm in his4_seq

    print(f"\n{left_path} ({len(left.seq)} bp):")
    for f in left.features:
        print(f"  [{int(f.location.start):5d}..{int(f.location.end):5d}] "
              f"{f.type:18s} {f.qualifiers.get('label', ['?'])[0]}")
    print(f"\n{right_path} ({len(right.seq)} bp):")
    for f in right.features:
        print(f"  [{int(f.location.start):5d}..{int(f.location.end):5d}] "
              f"{f.type:18s} {f.qualifiers.get('label', ['?'])[0]}")

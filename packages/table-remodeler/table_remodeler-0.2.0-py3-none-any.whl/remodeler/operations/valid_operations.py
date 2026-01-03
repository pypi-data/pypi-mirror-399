"""The valid operations for the remodeling tools."""

from remodeler.operations.factor_column_op import FactorColumnOp
from remodeler.operations.factor_hed_tags_op import FactorHedTagsOp
from remodeler.operations.factor_hed_type_op import FactorHedTypeOp
from remodeler.operations.merge_consecutive_op import MergeConsecutiveOp

from remodeler.operations.remove_columns_op import RemoveColumnsOp
from remodeler.operations.reorder_columns_op import ReorderColumnsOp
from remodeler.operations.remap_columns_op import RemapColumnsOp
from remodeler.operations.remove_rows_op import RemoveRowsOp
from remodeler.operations.rename_columns_op import RenameColumnsOp
from remodeler.operations.split_rows_op import SplitRowsOp
from remodeler.operations.summarize_column_names_op import SummarizeColumnNamesOp
from remodeler.operations.summarize_column_values_op import SummarizeColumnValuesOp
from remodeler.operations.summarize_definitions_op import SummarizeDefinitionsOp
from remodeler.operations.summarize_sidecar_from_events_op import SummarizeSidecarFromEventsOp
from remodeler.operations.summarize_hed_type_op import SummarizeHedTypeOp
from remodeler.operations.summarize_hed_tags_op import SummarizeHedTagsOp
from remodeler.operations.summarize_hed_validation_op import SummarizeHedValidationOp

#: Dictionary mapping operation names to their implementation classes.
#: Each key is a string operation name used in JSON specifications,
#: and each value is the corresponding operation class.
valid_operations = {
    "factor_column": FactorColumnOp,
    "factor_hed_tags": FactorHedTagsOp,
    "factor_hed_type": FactorHedTypeOp,
    "merge_consecutive": MergeConsecutiveOp,
    "remap_columns": RemapColumnsOp,
    "remove_columns": RemoveColumnsOp,
    "remove_rows": RemoveRowsOp,
    "rename_columns": RenameColumnsOp,
    "reorder_columns": ReorderColumnsOp,
    "split_rows": SplitRowsOp,
    "summarize_column_names": SummarizeColumnNamesOp,
    "summarize_column_values": SummarizeColumnValuesOp,
    "summarize_definitions": SummarizeDefinitionsOp,
    "summarize_hed_tags": SummarizeHedTagsOp,
    "summarize_hed_type": SummarizeHedTypeOp,
    "summarize_hed_validation": SummarizeHedValidationOp,
    "summarize_sidecar_from_events": SummarizeSidecarFromEventsOp,
}

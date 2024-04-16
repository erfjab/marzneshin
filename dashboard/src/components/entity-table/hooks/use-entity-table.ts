import {
    ColumnDef,
    OnChangeFn,
    PaginationState,
    getCoreRowModel,
    getPaginationRowModel,
    getSortedRowModel,
    useReactTable
} from "@tanstack/react-table";
import {
    UseRowSelectionReturn,
    UseSortingReturn,
    UseVisibilityReturn
} from ".";

interface UseEntityTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[]
    data: {
        entity: TData[]
        pageCount: number
    }
    sorting: UseSortingReturn
    visibility: UseVisibilityReturn
    rowSelection?: UseRowSelectionReturn
    pageIndex: number
    pageSize: number
    onPaginationChange: OnChangeFn<PaginationState>
}

export const useEntityTable = <TData, TValue>(
    {
        columns,
        data,
        sorting,
        visibility,
        rowSelection,
        pageIndex,
        pageSize,
        onPaginationChange
    }: UseEntityTableProps<TData, TValue>
) => useReactTable({
    data: data.entity,
    columns,
    manualPagination: true,
    pageCount: data.pageCount + 1,
    autoResetPageIndex: false,
    onPaginationChange,
    onSortingChange: sorting.setSorting,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onColumnVisibilityChange: visibility.setColumnVisibility,
    onRowSelectionChange: rowSelection && rowSelection.setSelectedRow,
    state: {
        sorting: sorting.sorting,
        columnVisibility: visibility.columnVisibility,
        pagination: { pageIndex: pageIndex - 1, pageSize },
        rowSelection: rowSelection ? rowSelection.selectedRow : {},
    },
})
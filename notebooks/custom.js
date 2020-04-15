// Format %%hy cells using scheme syntax highlighting.
IPython.CodeCell.options_default.highlight_modes['magic_text/x-scheme'] = {'reg':[/^%%hy/]} ;
IPython.notebook.events.one('kernel_ready.Kernel', function(){
  IPython.notebook.get_cells().map(function(cell){
    if (cell.cell_type == 'code'){ cell.auto_highlight(); } }) ;
});

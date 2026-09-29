param([string]$docx, [string]$pdf)
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    $d = $w.Documents.Open($docx, $false, $true)
    $d.Repaginate()
    $pages = $d.ComputeStatistics(2)
    "PAGES=$pages"
    $d.ExportAsFixedFormat($pdf, 17)
    $d.Close($false)
} finally {
    $w.Quit()
}

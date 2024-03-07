class HelloWorld < Formula
  desc "Simple program that outputs 'Hello, World!'"
  homepage "https://app.lizardbyte.devm"
  url "https://github.com/LizardByte/homebrew-release-action.git"
  version "0.0.1"

  def install
    # create hello world sh file with echo command
    (buildpath/"hello-world").write <<~EOS
    #!/bin/sh
    echo "Hello, World!"
    EOS

    # install the hello-world file to the bin directory
    bin.install "hello-world"
  end

  test do
    system "#{bin}/hello-world"
  end
end
# Created from LizardByte/homebrew-release-action@7ed82309b176395ef88a21c981326bad0acf1cc8

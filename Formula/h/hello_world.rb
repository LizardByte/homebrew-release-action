class HelloWorld < Formula
  desc "Simple program that outputs 'Hello, World!'"
  homepage "https://app.lizardbyte.dev"
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

    puts "buildpath: #{buildpath}"
  end

  test do
    system "#{bin}/hello-world"

    puts "testpath: #{testpath}"
  end
end
# Created from LizardByte/homebrew-release-action@c07722050650bd4eec5f7d97270bd5e38edc828a
